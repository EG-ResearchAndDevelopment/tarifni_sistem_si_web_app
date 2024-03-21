import os
import numpy as np
import pandas as pd
import json
import datetime

from consumer import Consumer
from utils import *


class Settlement():

    def __init__(self, smm: int = 0) -> None:
        # initialize the consumer
        self._consumer = Consumer(smm)

        self._output = {
            "ts_results": {
                "month_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "year": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "q_exceeded_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "tec_price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            },
            "block_billing_powers": [0, 0, 0, 0, 0],
            "connected_power": 0,
            "billing_power": 0,
            "consumer_type": "",
            "tariff_prices": dict(),
            "num_phases": 0,
            "num_tariffs": 0,
            "samooskrba": 0,
            "ERROR": 0
        }

    @property
    def consumer(self) -> Consumer:
        return self._consumer

    @property
    def smm(self) -> int:
        return self._smm

    @property
    def output(self) -> dict:
        return self.round_output(self._output, decimals=2)

    @smm.setter
    def smm(self, value):
        self._smm = value

    @consumer.setter
    def consumer(self, value):
        self._consumer = value

    @output.setter
    def output(self, value):
        self._output = value

    def __repr__(self) -> str:
        return "<Obracun(smm: int, start: pd.DatetimeIndex, end: pd.DatetimeIndex)>"

    def __str__(self) -> str:
        return "<Obracun(smartmeter id, start date, end date)>"

    def calculate_settlement(
        self,
        smm: int,
        timeseries_data: pd.DataFrame = None,
        tech_data: json = None,
        preprocess=True,
        calculate_blocks=False,
        override_year=False,
        include_vat=True,
    ) -> None:
        '''
            Function calculate_settlement calculates the settlement for the given consumer.
        '''

        # reset the output
        self.reset_output()

        # Value Added Tax (DDV)
        VAT = 1.22
        if not include_vat:
            VAT = 1

        # populate the base settlement data

        self.consumer.smm = smm

        self.consumer.load_consumer_data(timeseries_data=timeseries_data,
                                         tech_data=tech_data,
                                         preprocess=preprocess,
                                         calculate_blocks=calculate_blocks,
                                         override_year=override_year)

        # Handle errors
        if isinstance(self.consumer.smm_consumption, bool):
            # "No Data for this SMM!"
            self.output["ERROR"] = (200, "No Data for this SMM!")
            return self.output
        elif isinstance(self.consumer.smm_tech_data, bool):
            self.output["ERROR"] = (202,
                                    "Tehnical data could not be retrieved!")
            return self.output

        # Fill static parameters to the output
        self.output["connected_power"] = self.consumer.connected_power
        self.output["billing_power"] = self.consumer.billing_power
        self.output["num_phases"] = self.consumer.num_phases
        self.output["num_tariffs"] = self.consumer.num_tariffs
        self.output["consumer_type"] = self.consumer.consumer_type_id
        self.output["block_billing_powers"] = list(
            self.consumer.new_billing_powers)
        self.output["samooskrba"] = self.consumer.samooskrba
        self.output["tariff_prices"] = self.consumer.constants
        ts_year = self.consumer.smm_consumption

        # Calculate settlements
        if self.consumer.samooskrba:
            s_ove_spte_e = 0.
            s_omr_et = 0.
            s_omr_vt = 0.
            s_omr_mt = 0.
            s_e_et = 0.

            for iter_id, (month_num, ts_month) in enumerate(
                    ts_year.groupby(ts_year.index.month, sort=False)):
                dates_month = list(ts_month.index)
                year = dates_month[0].year
                Ps_month = np.array(ts_month.p)
                Jal_Ps_month = np.array(ts_month.q)
                es = Ps_month / 4
                Jal_es = Jal_Ps_month / 4

                new_omr_p, new_omr_e, new_pens, _ = self.omr_prices_new(
                    dates_month, Ps_month, es, Jal_es)

                (e_mt, e_vt, e_et), (
                    omr_p, omr_mt, omr_vt, omr_et, pens
                ), ove_spte_e, ove_spte_p, omr_q_exceeded_e = self.omr_prices_old(
                    dates_month, Ps_month, es, Jal_es)

                # self.output["e_mt"][month_num-1] = e_mt*CONST_DDV
                # self.output["e_vt"][iter_id] = e_vt*CONST_DDV
                self.output["ts_results"]["e_et"][iter_id] = e_et * VAT
                self.output["ts_results"]["omr_p"][iter_id] = omr_p * VAT
                self.output["ts_results"]["pens"][iter_id] = pens * VAT
                self.output["ts_results"]["new_pens"][iter_id] = new_pens * VAT
                self.output["ts_results"]["new_omr_p"][
                    iter_id] = new_omr_p * VAT
                self.output["ts_results"]["q_exceeded_e"][
                    iter_id] = omr_q_exceeded_e * VAT
                self.output["ts_results"]["omr_p"][iter_id] = omr_p * VAT
                self.output["ts_results"]["pens"][iter_id] = pens * VAT
                self.output["ts_results"]["new_pens"][iter_id] = new_pens * VAT
                self.output["ts_results"]["ove_spte_p"][
                    iter_id] = ove_spte_p * VAT
                self.output["ts_results"]["month_num"][iter_id] = month_num
                self.output["ts_results"]["year"][iter_id] = year
                s_ove_spte_e += ove_spte_e
                s_omr_et += omr_et
                s_e_et += e_et
            if s_omr_et < 0:
                s_e_et = 0.
                s_omr_et = 0.
                s_ove_spte_e = 0.

            for i in range(len(self.output["ts_results"]["month_num"])):
                self.output["ts_results"]["e_et"][i] = s_e_et / 12 * VAT
                self.output["ts_results"]["omr_mt"][i] = s_omr_mt / 12 * VAT
                self.output["ts_results"]["omr_vt"][i] = s_omr_vt / 12 * VAT
                self.output["ts_results"]["omr_et"][i] = s_omr_et / 12 * VAT
                self.output["ts_results"]["ove_spte_e"][
                    i] = s_ove_spte_e / 12 * VAT
        else:
            for iter_id, (month_num, ts_month) in enumerate(
                    ts_year.groupby(ts_year.index.month, sort=False)):
                dates_month = list(ts_month.index)
                # get year, month
                year = dates_month[0].year
                Ps_month = np.array(ts_month.p)
                Jal_Ps_month = np.array(ts_month.q)
                es = Ps_month / 4
                Jal_es = Jal_Ps_month / 4
                new_omr_p, new_omr_e, new_pens, _ = self.omr_prices_new(
                    dates_month, Ps_month, es, Jal_es)

                (e_mt, e_vt, e_et), (
                    omr_p, omr_mt, omr_vt, omr_et, pens
                ), ove_spte_e, ove_spte_p, omr_q_exceeded_e = self.omr_prices_old(
                    dates_month, Ps_month, es, Jal_es)

                self.output["ts_results"]["e_mt"][month_num - 1] = e_mt * VAT
                self.output["ts_results"]["e_vt"][iter_id] = e_vt * VAT
                self.output["ts_results"]["e_et"][iter_id] = e_et * VAT
                self.output["ts_results"]["omr_p"][iter_id] = omr_p * VAT
                self.output["ts_results"]["omr_mt"][
                    iter_id] = 0 if omr_mt < 0 else omr_mt * VAT
                self.output["ts_results"]["omr_vt"][
                    iter_id] = 0 if omr_vt < 0 else omr_vt * VAT
                self.output["ts_results"]["omr_et"][
                    iter_id] = 0 if omr_et < 0 else omr_et * VAT
                self.output["ts_results"]["q_exceeded_e"][
                    iter_id] = omr_q_exceeded_e * VAT
                self.output["ts_results"]["pens"][iter_id] = pens * VAT
                self.output["ts_results"]["new_omr_p"][
                    iter_id] = new_omr_p * VAT
                self.output["ts_results"]["new_omr_e"][
                    iter_id] = new_omr_e * VAT
                self.output["ts_results"]["new_pens"][iter_id] = new_pens * VAT
                self.output["ts_results"]["ove_spte_e"][
                    iter_id] = ove_spte_e * VAT
                self.output["ts_results"]["ove_spte_p"][
                    iter_id] = ove_spte_p * VAT
                self.output["ts_results"]["month_num"][iter_id] = month_num
                self.output["ts_results"]["year"][iter_id] = year

    def omr_values_new(self, power_ts, energy_ts, q_energies, tariff_mask):
        # jalova
        q_exceeded_e = np.sum(
            (np.abs(q_energies) - 0.32868 * np.abs(energy_ts)) *
            ((np.abs(q_energies) - 0.32868 * np.abs(energy_ts)) > 0))

        # omreznina vrednosti
        powers_masked = tariff_mask * power_ts
        vrednost_e = np.matmul(tariff_mask, energy_ts)

        return powers_masked, vrednost_e, q_exceeded_e

    def omr_prices_new(self, dates, powers, energies, q_energies):
        """
        Funkcija izracuna omreznino za mesec po novem sistemu
        """
        Fex = 0.9  # faktor presežene obračunske moči
        obr_powers = self.consumer.new_billing_powers

        tariff_mask = individual_tariff_times(dates)  # 5×N array

        powers_masked, energy_consumption, q_exceeded_e = self.omr_values_new(
            powers, energies, q_energies, tariff_mask)

        block_powers_penalties = np.zeros(5)
        for i in range(len(powers_masked)):  # gre prek vseh blokov
            obr_power = obr_powers[i]
            powers_blok = powers_masked[i]
            power_exceeded = (powers_blok - obr_power) * (powers_blok
                                                          > obr_power)
            block_powers_penalties[i] = Fex * np.sqrt(sum(power_exceeded**2))

        consumer_tariffs = self.consumer.constants
        # izracun penalov
        powers_penalties = np.sum(block_powers_penalties *
                                  consumer_tariffs["cene_moci"])
        # izracun za jalovo energijo
        omr_q_exceeded_e = q_exceeded_e * consumer_tariffs["q_exc"]
        # izracun za energijo
        omr_energy = np.sum(energy_consumption * (energy_consumption > 0) *
                            (consumer_tariffs["tarife_prenos"] +
                             consumer_tariffs["tarife_distr"]))

        # izracun za moč
        M = dates[0].month
        if M in [1, 2, 11, 12]:
            omr_p = sum(obr_powers * consumer_tariffs["cene_moci"])
        else:
            omr_p = sum(obr_powers[1:] * consumer_tariffs["cene_moci"][1:])

        return omr_p, omr_energy, powers_penalties, omr_q_exceeded_e

    def omr_values_old(self, dates, energies, q_energies):
        u_vt = construct_high_tariff_time_mask(dates)

        obr_vt = (u_vt * energies).sum()
        obr_mt = ((-1 * (u_vt - 1)) * energies).sum()
        obr_et = (energies).sum()

        q_exceeded_e = np.sum(
            (np.abs(q_energies) - 0.32868 * np.abs(energies)) *
            ((np.abs(q_energies) - 0.32868 * np.abs(energies)) > 0))

        return obr_vt, obr_mt, obr_et, q_exceeded_e

    def omr_prices_old(self, dates, powers, energies, q_energies):
        """
        Funkcija izračuna obračun položnice po starem principu
        """
        consumer_tariffs = self.consumer.constants
        consumer_type_id = int(self.consumer.consumer_type_id)

        obr_vt, obr_mt, obr_et, q_exceeded_e = self.omr_values_old(
            dates, energies, q_energies)

        powers = powers * (powers > 0)

        omr_q_exceeded_e = q_exceeded_e * consumer_tariffs["q_exc"]
        if consumer_type_id == 1:  # GOSPODINJSKI ODJEMALEC
            # OMREZNINA
            omr_vt = obr_vt * consumer_tariffs["omr_vt"]
            omr_mt = obr_mt * consumer_tariffs["omr_mt"]
            omr_et = obr_et * consumer_tariffs["omr_et"]
            omr_p = self.consumer.billing_power * \
                consumer_tariffs["omr_obr_p"]

            # ENERGIJA
            e_vt = obr_vt * consumer_tariffs["energija"]["e_vt"]
            e_mt = obr_mt * consumer_tariffs["energija"]["e_mt"]
            e_et = obr_et * consumer_tariffs["energija"]["e_et"]

            # OVE
            prispevek_ove = consumer_tariffs["dajatve"]["prispevek_ove"]
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]
            ove_spte_p = self.consumer.billing_power * prispevek_ove
            if self.consumer.samooskrba:
                ove_spte_e = (delovanje_operaterja + trosarina) * obr_et
            else:
                ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_et

            return (e_mt, e_vt,
                    e_et), (omr_p, omr_mt, omr_vt, omr_et,
                            0), ove_spte_e, ove_spte_p, omr_q_exceeded_e

        elif consumer_type_id == 2:  # ODJEM NA NN BREZ MERJENE MOČI    # mali poslovni odjemalci
            obr_power = self.consumer.billing_power  # obračunska moč (W)

            # OMREZNINA
            powers_exceeded = obr_power - self.consumer.connected_power
            if powers_exceeded > 0:
                powers_penalty_price = powers_exceeded * pen
            else:
                powers_penalty_price = 0

            omr_vt = obr_vt * consumer_tariffs["omr_vt"]
            omr_mt = obr_mt * consumer_tariffs["omr_mt"]
            omr_et = obr_et * consumer_tariffs["omr_et"]
            omr_p = self.consumer.billing_power * \
                consumer_tariffs["omr_obr_p"]

            # ENERGIJA
            e_vt = obr_vt * consumer_tariffs["energija"]["e_vt"]
            e_mt = obr_mt * consumer_tariffs["energija"]["e_mt"]
            e_et = obr_et * consumer_tariffs["energija"]["e_et"]

            # OVE
            prispevek_ove = consumer_tariffs["dajatve"]["prispevek_ove"]
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]

            ove_spte_p = self.consumer.billing_power * prispevek_ove
            # if self.consumer.connection_scheme == "PS.3A":  # preveriti če je ok
            #     ove_spte_e = (delovanje_operaterja + trosarina) * obr_et
            # else:
            ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_et

            return (e_mt, e_vt, e_et), (
                omr_p, omr_mt, omr_vt, omr_et,
                powers_penalty_price), ove_spte_e, ove_spte_p, omr_q_exceeded_e

        elif consumer_type_id == 3:  # ODJEM NA NN Z MERJENJEM MOČI
            obrat_ure_high = self.consumer.operating_hours >= 2500
            obr_power = round(settlement_power(dates, powers))

            # OMREZNINA
            if self.consumer.bus_bar:
                if obrat_ure_high:
                    obr_moc = consumer_tariffs["obrat_ure_high"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_high"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_high"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_high"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_high"][
                        "prispevek_ove"]
                else:
                    obr_moc = consumer_tariffs["obrat_ure_low"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_low"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_low"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_low"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_low"][
                        "prispevek_ove"]
            else:
                if obrat_ure_high:
                    obr_moc = consumer_tariffs["obrat_ure_high"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_high"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_high"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_high"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_high"][
                        "prispevek_ove"]
                else:
                    obr_moc = consumer_tariffs["obrat_ure_low"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_low"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_low"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_low"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_low"][
                        "prispevek_ove"]

            omr_p = obr_moc * obr_power
            powers_exceeded = obr_power - self.consumer.connected_power
            if powers_exceeded > 0:
                powers_penalty_price = powers_exceeded * pen
            else:
                powers_penalty_price = 0

            omr_vt = obr_vt * omr_vt
            omr_mt = obr_mt * omr_mt
            omr_et = 0.

            # ENERGIJA
            e_vt = obr_vt * consumer_tariffs["energija"]["e_vt"]
            e_mt = obr_mt * consumer_tariffs["energija"]["e_mt"]
            e_et = obr_et * consumer_tariffs["energija"]["e_et"]

            # OVE
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]

            ove_spte_p = self.consumer.billing_power * prispevek_ove
            # if self.consumer.connection_scheme == "PS.3A":  # preveriti če je ok
            #     ove_spte_e = (delovanje_operaterja + trosarina) * obr_et
            # else:
            ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_et

            return (e_mt, e_vt, e_et), (
                omr_p, omr_mt, omr_vt, omr_et,
                powers_penalty_price), ove_spte_e, ove_spte_p, omr_q_exceeded_e

        elif consumer_type_id == 4:  # ODJEM NA SN OD 1 kV DO 35 kV
            obrat_ure_high = self.consumer.operating_hours >= 2500
            obr_power = round(
                settlement_power(dates, powers, self.consumer.koo_times))

            # OMREZNINA
            if self.consumer.bus_bar:
                if obrat_ure_high:
                    obr_moc = consumer_tariffs["obrat_ure_high"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_high"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_high"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_high"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_high"][
                        "prispevek_ove"]
                else:
                    obr_moc = consumer_tariffs["obrat_ure_low"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_low"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_low"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_low"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_low"][
                        "prispevek_ove"]
            else:
                if obrat_ure_high:
                    obr_moc = consumer_tariffs["obrat_ure_high"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_high"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_high"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_high"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_high"][
                        "prispevek_ove"]
                else:
                    obr_moc = consumer_tariffs["obrat_ure_low"]["omr_obr_p"]
                    omr_vt = consumer_tariffs["obrat_ure_low"]["omr_vt"]
                    omr_mt = consumer_tariffs["obrat_ure_low"]["omr_mt"]
                    pen = consumer_tariffs["obrat_ure_low"]["pen"]
                    prispevek_ove = consumer_tariffs["obrat_ure_low"][
                        "prispevek_ove"]

            omr_p = obr_moc * obr_power
            powers_exceeded = obr_power - self.consumer.connected_power
            if powers_exceeded > 0:
                powers_penalty_price = powers_exceeded * pen
            else:
                powers_penalty_price = 0

            omr_vt = obr_vt * omr_vt
            omr_mt = obr_mt * omr_mt
            omr_et = 0

            # ENERGIJA
            obr_et = energies.sum()
            if obr_et < 20000:
                e_cena = consumer_tariffs["energija"]["20000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["20000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000"]["trosarina"]
            elif obr_et < 500000:
                e_cena = consumer_tariffs["energija"]["500000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["500000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["500000"]["trosarina"]
            elif obr_et < 2000000:
                e_cena = consumer_tariffs["energija"]["2000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["2000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["2000000"][
                    "trosarina"]
            elif obr_et < 20000000:
                e_cena = consumer_tariffs["energija"]["20000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["20000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000000"][
                    "trosarina"]
            elif obr_et < 70000000:
                e_cena = consumer_tariffs["energija"]["70000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["70000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["70000000"][
                    "trosarina"]
            elif obr_et < 150000000:
                e_cena = consumer_tariffs["energija"]["150000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["150000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["150000000"][
                    "trosarina"]
            else:
                e_cena = consumer_tariffs["energija"]["ostalo"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["ostalo"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["ostalo"]["trosarina"]
            e_vt = (obr_vt / 1000) * e_cena
            e_mt = (obr_mt / 1000) * e_cena
            e_et = (obr_et / 1000) * e_cena

            # OVE
            ove_spte_p = self.consumer.billing_power * prispevek_ove
            ove_spte_e = (dajatve + trosarina) * (obr_et / 1000)

            return (e_mt, e_vt, e_et), (
                omr_p, omr_mt, omr_vt, omr_et,
                powers_penalty_price), ove_spte_e, ove_spte_p, omr_q_exceeded_e
        else:
            return (0, 0, 0), (0, 0, 0, 0, 0), 0, 0, 0

    def round_output(self, output: dict, decimals: int = 6) -> dict:
        """
        Function round_output rounds the output dictionary to the given number of decimals.
        """

        for key in output["ts_results"].keys():
            output["ts_results"][key] = list(
                round(value, decimals) for value in output["ts_results"][key])

        return output

    def reset_output(self):
        """
        the function resets the output.
        """
        self.output = {
            "ts_results": {
                "month_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "year": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "q_exceeded_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "tec_price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            },
            "block_billing_powers": [0, 0, 0, 0, 0],
            "connected_power": 0,
            "billing_power": 0,
            "consumer_type": "",
            "tariff_prices": dict(),
            "num_phases": 0,
            "num_tariffs": 0,
            "samooskrba": 0,
            "ERROR": 0
        }
