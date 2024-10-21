import datetime
import logging
import json
import os

import numpy as np
import pandas as pd

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
        return self.round_output(self._output, decimals=3)

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

    def round_output(self, output: dict, decimals: int = 6) -> dict:
        """
        Function round_output rounds the output dictionary to the given number of decimals.
        """

        for key in output["ts_results"].keys():
            output["ts_results"][key] = list(
                round(value, decimals) for value in output["ts_results"][key])

        return output

    def calculate_settlement(
        self,
        timeseries_data: pd.DataFrame = None,
        tech_data: json = None,
        preprocess=True,
        calculate_obr_p_values=False,
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

        logging.info("Loading consumer data")
        # populate the base settlement data
        self.consumer.load_consumer_data(
            timeseries_data=timeseries_data,
            tech_data=tech_data,
            preprocess=preprocess,
            calculate_obr_p_values=calculate_obr_p_values,
            override_year=override_year)
        logging.info("Consumer data loaded")

        # Handle errors
        if isinstance(self.consumer.smm_consumption, bool):
            # "No Data for this SMM!"
            self.output["ERROR"] = (200, "No Data for this SMM!")
            return self.output
        elif isinstance(self.consumer.smm_tech_data, bool):
            self.output["ERROR"] = (202,
                                    "Tehnical data could not be retrieved!")
            return self.output

        logging.info("Setting up the consumer data")
        # Fill static parameters to the output
        self.output["connected_power"] = self.consumer.connected_power
        self.output["billing_power"] = self.consumer.billing_power
        self.output["num_phases"] = self.consumer.num_phases
        self.output["num_tariffs"] = self.consumer.num_tariffs
        self.output["consumer_type"] = self.consumer.consumer_type_id
        self.output["block_billing_powers"] = [
            round(num, 1) for num in list(self.consumer.new_billing_powers)
        ]
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
            s_omr_new_e = 0.
            yearly_energy = 0
            logging.info("Calculating settlements")
            for iter_id, (month_num, ts_month) in enumerate(
                    ts_year.groupby(ts_year.index.month, sort=False)):
                dates_month = list(ts_month.index)
                year = dates_month[0].year
                Ps_month = np.array(ts_month.p)
                Jal_Ps_month = np.array(ts_month.q)
                es = Ps_month / 4
                yearly_energy += sum(es)
                Jal_es = Jal_Ps_month / 4

                (new_omr_p, new_omr_e, new_pens, _), (new_ove_spte_e, new_ove_spte_p) = self.prices_new(
                    dates_month, Ps_month, es, Jal_es)

                (e_mt, e_vt, e_et), (
                    omr_p, omr_mt, omr_vt, omr_et, pens
                ), ove_spte_e, ove_spte_p, omr_q_exceeded_e = self.prices_old(
                    dates_month, Ps_month, es, Jal_es)
                self.output["ts_results"]["e_et"][iter_id] = e_et * VAT
                self.output["ts_results"]["omr_p"][iter_id] = omr_p * VAT
                self.output["ts_results"]["pens"][iter_id] = pens * VAT
                self.output["ts_results"]["new_pens"][iter_id] = new_pens * VAT
                self.output["ts_results"]["new_omr_p"][
                    iter_id] = new_omr_p * VAT
                self.output["ts_results"]["new_omr_e"][
                    iter_id] = new_omr_e * VAT
                self.output["ts_results"]["q_exceeded_e"][
                    iter_id] = omr_q_exceeded_e * VAT
                self.output["ts_results"]["omr_p"][iter_id] = omr_p * VAT
                self.output["ts_results"]["pens"][iter_id] = pens * VAT
                self.output["ts_results"]["new_pens"][iter_id] = new_pens * VAT
                self.output["ts_results"]["ove_spte_p"][
                    iter_id] = new_ove_spte_p * VAT
                self.output["ts_results"]["month_num"][iter_id] = month_num
                self.output["ts_results"]["year"][iter_id] = year
                s_ove_spte_e += new_ove_spte_e
                s_omr_et += omr_et
                s_omr_new_e += new_omr_e
                s_e_et += e_et

            if yearly_energy < 0:
                s_e_et = 0.
                s_omr_et = 0.
                s_ove_spte_e = 0.
                s_omr_new_e = 0.

            for i in range(len(self.output["ts_results"]["month_num"])):
                self.output["ts_results"]["new_omr_e"][
                    i] = s_omr_new_e / 12 * VAT
                self.output["ts_results"]["ove_spte_e"][
                    i] = s_ove_spte_e / 12 * VAT
                self.output["ts_results"]["e_et"][i] = s_e_et / 12 * VAT
                self.output["ts_results"]["omr_mt"][i] = s_omr_mt / 12 * VAT
                self.output["ts_results"]["omr_vt"][i] = s_omr_vt / 12 * VAT
                self.output["ts_results"]["omr_et"][i] = s_omr_et / 12 * VAT

        else:
            logging.info("Calculating settlements")
            for iter_id, (month_num, ts_month) in enumerate(
                    ts_year.groupby(ts_year.index.month, sort=False)):
                logging.info("Calculating settlements for month %s", month_num)
                dates_month = list(ts_month.index)
                # get year, month
                year = dates_month[0].year
                Ps_month = np.array(ts_month.p)
                Jal_Ps_month = np.array(ts_month.q)
                es = Ps_month / 4
                Jal_es = Jal_Ps_month / 4
                logging.info("Calculating new prices")
                (new_omr_p, new_omr_e, new_pens, new_omr_q_exceeded_e), (new_ove_spte_e, new_ove_spte_p) = self.prices_new(
                    dates_month, Ps_month, es, Jal_es)
                logging.info("Calculating old prices")
                (e_mt, e_vt, e_et), (
                    omr_p, omr_mt, omr_vt, omr_et, pens
                ), ove_spte_e, ove_spte_p, omr_q_exceeded_e = self.prices_old(
                    dates_month, Ps_month, es, Jal_es)
                logging.info("Setting the output")

                if e_mt < 0:
                    e_mt = 0
                if e_vt < 0:
                    e_vt = 0
                if e_et < 0:
                    e_et = 0
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
                    iter_id] = new_ove_spte_e * VAT
                self.output["ts_results"]["ove_spte_p"][
                    iter_id] = new_ove_spte_p * VAT
                self.output["ts_results"]["month_num"][iter_id] = month_num
                self.output["ts_results"]["year"][iter_id] = year
                logging.info("Settlements calculated for month %s", month_num)
        return self.output
    
    def omr_values_new(self, power_ts, energy_ts, q_energies, tariff_mask):
        # jalova
        q_exceeded_e = np.sum(
            (np.abs(q_energies) - 0.32868 * np.abs(energy_ts)) *
            ((np.abs(q_energies) - 0.32868 * np.abs(energy_ts)) > 0))

        # omreznina vrednosti
        powers_masked = tariff_mask * power_ts * (power_ts > 0)
        energy_ts = energy_ts * (energy_ts > 0)
        vrednost_e = np.matmul(tariff_mask, energy_ts)

        return powers_masked, vrednost_e, q_exceeded_e

    def taxes(self, powers, season, consumer_tariffs):
        """
        Funkcija izračuna dajatve
        """
        consumer_type_id = int(self.consumer.consumer_type_id)
        # calculate

        # get max power in the block
        if season == 0:
            max_power = np.max(powers[1])
        else:
            max_power = np.max(powers[0])
        ove_spte_p = max_power * consumer_tariffs["dajatve"]["prispevek_ove"]

        energy = np.sum(powers) * 0.25
        if consumer_type_id < 4:
            if self.consumer.samooskrba:
                ove_spte_e = (consumer_tariffs["dajatve"]["delovanje_operaterja"] +
                            consumer_tariffs["dajatve"]["trosarina"]) * energy
            else:
                ove_spte_e = (consumer_tariffs["dajatve"]["delovanje_operaterja"] +
                            consumer_tariffs["dajatve"]["energ_ucinkovitost"] +
                            consumer_tariffs["dajatve"]["trosarina"]) * energy
        else:
            if energy < 20000:
                dajatve = consumer_tariffs["energija"]["20000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000"]["trosarina"]
            elif energy < 500000:
                dajatve = consumer_tariffs["energija"]["500000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["500000"]["trosarina"]
            elif energy < 2000000:
                dajatve = consumer_tariffs["energija"]["2000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["2000000"][
                    "trosarina"]
            elif energy < 20000000:
                dajatve = consumer_tariffs["energija"]["20000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000000"][
                    "trosarina"]
            elif energy < 70000000:
                dajatve = consumer_tariffs["energija"]["70000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["70000000"][
                    "trosarina"]
            elif energy < 150000000:
                dajatve = consumer_tariffs["energija"]["150000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["150000000"][
                    "trosarina"]
            else:
                dajatve = consumer_tariffs["energija"]["ostalo"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["ostalo"]["trosarina"]
            ove_spte_e = (dajatve + trosarina) * (energy / 1000)

        return ove_spte_p, ove_spte_e


        #
    def prices_new(self, dates, powers, energies, q_energies):
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

        # izracun za moč in dajatve
        M = dates[0].month
        if M in [1, 2, 11, 12]:
            omr_p = sum(obr_powers * consumer_tariffs["cene_moci"])
            ove_spte_p, ove_spte_e = self.taxes(powers_masked, season=1, consumer_tariffs=consumer_tariffs)
        else:
            omr_p = sum(obr_powers[1:] * consumer_tariffs["cene_moci"][1:])
            ove_spte_p, ove_spte_e = self.taxes(powers_masked, season=0, consumer_tariffs=consumer_tariffs)
        

        return (omr_p, omr_energy, powers_penalties, omr_q_exceeded_e), (ove_spte_e, ove_spte_p)

    def omr_values_old(self, dates, energies, q_energies):
        u_vt = construct_high_tariff_time_mask(dates)

        logging.info(u_vt)
        if not self.consumer.samooskrba:
            energies = energies * (energies > 0)
        obr_vt = (u_vt * energies).sum()
        obr_mt = ((u_vt-1)**2 * energies).sum()
        obr_et = (energies).sum()

        q_exceeded_e = np.sum(
            (np.abs(q_energies) - 0.32868 * np.abs(energies)) *
            ((np.abs(q_energies) - 0.32868 * np.abs(energies)) > 0))

        return obr_vt, obr_mt, obr_et, q_exceeded_e

    def prices_old(self, dates, powers, energies, q_energies):
        """
        Funkcija izračuna obračun položnice po starem principu
        """
        logging.info("Calculating prices for old system")
        consumer_tariffs = self.consumer.constants
        consumer_type_id = int(self.consumer.consumer_type_id)
    
        logging.info("Calculating omr old values")
        obr_vt, obr_mt, obr_et, q_exceeded_e = self.omr_values_old(
            dates, energies, q_energies)
        logging.info("Calculating omr old values done")
        powers = powers * (powers > 0)

        logging.info("Calculating prices for old system")
        omr_q_exceeded_e = q_exceeded_e * consumer_tariffs["q_exc"]
        if consumer_type_id == 1:  # GOSPODINJSKI ODJEMALEC
            # OMREZNINA
            logging.info("Calculating network")
            omr_vt = obr_vt * consumer_tariffs["omr_vt"]
            omr_mt = obr_mt * consumer_tariffs["omr_mt"]
            omr_et = obr_et * consumer_tariffs["omr_et"]
            omr_p = self.consumer.billing_power * \
                consumer_tariffs["omr_obr_p"]

            # ENERGIJA
            logging.info("Calculating energy")
            e_vt = obr_vt * consumer_tariffs["energija"]["e_vt"]
            e_mt = obr_mt * consumer_tariffs["energija"]["e_mt"]
            e_et = obr_et * consumer_tariffs["energija"]["e_et"]

            # OVE
            logging.info("Calculating OVESPTE")
            prispevek_ove = consumer_tariffs["dajatve"]["prispevek_ove"]
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]
            ove_spte_p = self.consumer.billing_power * prispevek_ove

            logging.info("Calculating taxes")
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
            if self.consumer.samooskrba:  # preveriti če je ok
                ove_spte_e = (delovanje_operaterja + trosarina) * obr_et
            else:
                ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_et

            return (e_mt, e_vt, e_et), (
                omr_p, omr_mt, omr_vt, omr_et,
                0), ove_spte_e, ove_spte_p, omr_q_exceeded_e

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


    def reset_output(self):
        """
        the function resets the output.
        """
        self._output = {
            "ts_results": {
                "month_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "year": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "e_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_mt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_vt": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "omr_et": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "q_exceeded_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_omr_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "new_pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "tec_price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "ove_spte_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
