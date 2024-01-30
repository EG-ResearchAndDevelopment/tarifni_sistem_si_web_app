import os
import numpy as np
import pandas as pd
import json

from consumer import Consumer
from utils import *
from read_elektro_csv import read_moj_elektro_csv
from consumer import Consumer


class Settlement():

    def __init__(self, smm: int = 0) -> None:
        # initialize the consumer
        self._consumer = Consumer(smm)

        self._output = {
            "month_num": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "year": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_MT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_VT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_ET": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_moc": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_MT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_VT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_ET": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_jal": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_jal": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_omr_moc": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_omr_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_Pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "tec_price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "ove_spte_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "ove_spte_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "obracunske_moci": [0, 0, 0, 0, 0],
            "prikljucna_moc": 0,
            "obracunska_moc": 0,
            "vrsta_odjema": "",
            "postavke": dict(),
            "obracunska_moc": 0,
            "stevilo_faz": 0,
            "stevilo_tarif": 0,
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
        return self._output

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
                                         preprocess=preprocess)

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
        self.output["prikljucna_moc"] = self.consumer.prikljucna_moc
        self.output["obracunska_moc"] = self.consumer.obracunska_moc
        self.output["stevilo_faz"] = self.consumer.stevilo_faz
        self.output["stevilo_tarif"] = self.consumer.trenutno_stevilo_tarif
        self.output["vrsta_odjema"] = self.consumer.user_id
        self.output["obracunske_moci"] = list(self.consumer.obracunske_moci)
        self.output["samooskrba"] = self.consumer.samooskrba
        self.output["postavke"] = self.consumer.constants
        ts_year = self.consumer.smm_consumption

        # Calculate settlements
        if self.consumer.samooskrba:
            s_ove_spte_e = 0.
            s_omr_ET = 0.
            s_omr_VT = 0.  # TODO: Preveri če je ok
            s_omr_MT = 0.  # TODO: Preveri če je ok
            s_e_ET = 0.

            for iter_id, (month_num, ts_month) in enumerate(
                    ts_year.groupby(ts_year.index.month, sort=False)):
                dates_month = list(ts_month.index)
                year = dates_month[0].year
                Ps_month = np.array(ts_month.p)
                Jal_Ps_month = np.array(ts_month.q)
                es = Ps_month / 4
                Jal_es = Jal_Ps_month / 4

                new_omr_moc, new_omr_e, new_Pens, omr_wqex_new = self.obracun_omr_new(
                    dates_month, Ps_month, Jal_Ps_month, es, Jal_es)

                (e_MT, e_VT, e_ET), (
                    omr_moc, omr_MT, omr_VT, omr_ET, Pens
                ), ove_spte_e, ove_spte_p, omr_wqex = self.obracun_omr_old(
                    dates_month, Ps_month, Jal_Ps_month, es, Jal_es)

                # self.output["e_MT"][month_num-1] = e_MT*CONST_DDV
                # self.output["e_VT"][iter_id] = e_VT*CONST_DDV
                self.output["e_ET"][iter_id] = e_ET * VAT
                self.output["omr_moc"][iter_id] = omr_moc * VAT
                self.output["Pens"][iter_id] = Pens * VAT
                self.output["new_Pens"][iter_id] = new_Pens * VAT
                self.output["new_omr_moc"][iter_id] = new_omr_moc * VAT
                self.output["omr_jal"][iter_id] = omr_wqex * VAT
                self.output["omr_moc"][iter_id] = omr_moc * VAT
                self.output["Pens"][iter_id] = Pens * VAT
                self.output["new_Pens"][iter_id] = new_Pens * VAT
                self.output["ove_spte_p"][iter_id] = ove_spte_p * VAT
                self.output["month_num"][iter_id] = month_num
                self.output["year"][iter_id] = year
                s_ove_spte_e += ove_spte_e
                s_omr_ET += omr_ET
                s_e_ET += e_ET
            if s_omr_ET < 0:
                s_e_ET = 0.
                s_omr_ET = 0.
                s_ove_spte_e = 0.

            for i in range(len(self.output["month_num"])):
                # self.output["e_MT"][i] = s_e_MT/12*CONST_DDV
                # self.output["e_VT"][i] = s_e_VT/12*CONST_DDV
                self.output["e_ET"][i] = s_e_ET / 12 * VAT
                self.output["omr_MT"][i] = s_omr_MT / 12 * VAT
                self.output["omr_VT"][i] = s_omr_VT / 12 * VAT
                self.output["omr_ET"][i] = s_omr_ET / 12 * VAT
                self.output["ove_spte_e"][i] = s_ove_spte_e / 12 * VAT
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
                new_omr_moc, new_omr_e, new_Pens, omr_wqex_new = self.obracun_omr_new(
                    dates_month, Ps_month, Jal_Ps_month, es, Jal_es)

                (e_MT, e_VT, e_ET), (
                    omr_moc, omr_MT, omr_VT, omr_ET, Pens
                ), ove_spte_e, ove_spte_p, omr_wqex = self.obracun_omr_old(
                    dates_month, Ps_month, Jal_Ps_month, es, Jal_es)

                self.output["e_MT"][month_num - 1] = e_MT * VAT
                self.output["e_VT"][iter_id] = e_VT * VAT
                self.output["e_ET"][iter_id] = e_ET * VAT
                self.output["omr_moc"][iter_id] = omr_moc * VAT
                self.output["omr_MT"][iter_id] = omr_MT * VAT
                self.output["omr_VT"][iter_id] = omr_VT * VAT
                self.output["omr_ET"][iter_id] = omr_ET * VAT
                self.output["omr_jal"][iter_id] = omr_wqex * VAT
                self.output["Pens"][iter_id] = Pens * VAT
                self.output["new_omr_moc"][iter_id] = new_omr_moc * VAT
                self.output["new_omr_e"][iter_id] = new_omr_e * VAT
                self.output["new_Pens"][iter_id] = new_Pens * VAT
                self.output["ove_spte_e"][iter_id] = ove_spte_e * VAT
                self.output["ove_spte_p"][iter_id] = ove_spte_p * VAT
                self.output["month_num"][iter_id] = month_num
                self.output["year"][iter_id] = year

    def vrednosti_omr_new(self, Ps, es, Jal_es, tariff_mask):
        # jalova
        wqex = np.sum((np.abs(Jal_es) - 0.32868 * np.abs(es)) *
                      ((np.abs(Jal_es) - 0.32868 * np.abs(es)) > 0))

        # omreznina vrednosti
        Ps_masked = tariff_mask * Ps
        vrednost_e = np.matmul(tariff_mask, es)

        return Ps_masked, vrednost_e, wqex

    def obracun_omr_new(self,
                        dates,
                        Ps,
                        Jal_Ps,
                        es,
                        Jal_es,
                        only_calculate_energy: bool = False):
        """
        Funkcija izracuna omreznino za mesec po novem sistemu
        """
        Fex = 0.9  # faktor presežene obračunske moči
        obr_Ps = self.consumer.obracunske_moci
        tariff_mask = individual_tariff_times(dates)  # 5×N array

        Ps_masked, vrednosti_e, wqex = self.vrednosti_omr_new(
            Ps, es, Jal_es, tariff_mask)

        Pens = np.zeros(5)
        for i in range(len(Ps_masked)):  # gre prek vseh blokov
            obr_P = obr_Ps[i]
            Ps_blok = Ps_masked[i]
            Pex = (Ps_blok - obr_P) * (Ps_blok > obr_P)
            Pens[i] = Fex * np.sqrt(sum(Pex**2))
            # Pens += Fex*np.sqrt(sum(Pex**2))*cene_moci[i]

        if only_calculate_energy:
            return obr_Ps, vrednosti_e, Pens, wqex

        consumer_tariffs = self.consumer.constants
        print(consumer_tariffs)
        # izracun penalov
        Pens = np.sum(Pens * consumer_tariffs["cene_moci"])
        # izracun za jalovo energijo
        omr_wqex = wqex * consumer_tariffs["sp_jal_energ"]
        # izracun za energijo
        omr_e = np.sum(
            vrednosti_e * (vrednosti_e > 0) *
            (consumer_tariffs["tarife_P"] + consumer_tariffs["tarife_D"]))

        # izracun za moč
        M = dates[0].month
        if M in [1, 2, 11, 12]:
            omr_moc = sum(obr_Ps * consumer_tariffs["cene_moci"])
        else:
            omr_moc = sum(obr_Ps[1:] * consumer_tariffs["cene_moci"][1:])

        return omr_moc, omr_e, Pens, omr_wqex

    def vrednosti_omr_old(self, dates, Ps, Jal_Ps, es, Jal_es):
        u_VT = high_tariff_time(dates)

        obr_VT = (u_VT * es).sum()
        obr_MT = ((-1 * (u_VT - 1)) * es).sum()
        # obr_ET = (es*(es > 0)).sum()
        obr_ET = (es).sum()

        wqex = np.sum((np.abs(Jal_es) - 0.32868 * np.abs(es)) *
                      ((np.abs(Jal_es) - 0.32868 * np.abs(es)) > 0))


        return obr_VT, obr_MT, obr_ET, wqex

    def obracun_omr_old(self,
                        dates,
                        Ps,
                        Jal_Ps,
                        es,
                        Jal_es,
                        only_calculate_energy: bool = False):
        """
        Funkcija izračuna obračun položnice po starem principu
        """
        consumer_tariffs = self.consumer.constants
        odjID = int(self.consumer.user_id)

        obr_VT, obr_MT, obr_ET, wqex = self.vrednosti_omr_old(
            dates, Ps, Jal_Ps, es, Jal_es)
        if only_calculate_energy:
            return (obr_VT, obr_MT, obr_ET), (0, 0, 0, 0, 0), 0, 0, wqex

        Ps = Ps * (Ps > 0)

        omr_wqex = wqex * consumer_tariffs["sp_jal_energ"]
        if odjID == 1:  # GOSPODINJSKI ODJEMALEC
            # OMREZNINA
            omr_VT = obr_VT * consumer_tariffs["omrez_VT"]
            omr_MT = obr_MT * consumer_tariffs["omrez_MT"]
            omr_ET = obr_ET * consumer_tariffs["omrez_ET"]
            omr_moc = self.consumer.obracunska_moc * \
                consumer_tariffs["sp_obr_moc"]

            # ENERGIJA
            e_VT = obr_VT * consumer_tariffs["energija"]["energ_VT"]
            e_MT = obr_MT * consumer_tariffs["energija"]["energ_MT"]
            e_ET = obr_ET * consumer_tariffs["energija"]["energ_ET"]

            # OVE
            prispevek_ove = consumer_tariffs["dajatve"]["prispevek_ove"]
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]


            ove_spte_p = self.consumer.obracunska_moc * prispevek_ove
            if self.consumer.samooskrba:  # preveriti če je ok
                ove_spte_e = (delovanje_operaterja + trosarina) * obr_ET
            else:
                ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_ET

            return (e_MT, e_VT, e_ET), (omr_moc, omr_MT, omr_VT, omr_ET,
                                        0), ove_spte_e, ove_spte_p, omr_wqex

        elif odjID == 4:  # ODJEM NA SN OD 1 kV DO 35 kV
            zbiralke = self.consumer.zbiralke
            T_v = self.consumer.ObratovalneUre >= 2500
            obr_P = settlement_power(dates, Ps)

            # OMREZNINA
            if zbiralke:
                if T_v:
                    sp_obr_moc = consumer_tariffs["T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["T_v"]["omrez_MT"]
                    pen = consumer_tariffs["T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["T_v"]["prispevek_ove"]
                else:
                    sp_obr_moc = consumer_tariffs["not_T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["not_T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["not_T_v"]["omrez_MT"]
                    pen = consumer_tariffs["not_T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["not_T_v"][
                        "prispevek_ove"]
            else:
                if T_v:
                    sp_obr_moc = consumer_tariffs["T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["T_v"]["omrez_MT"]
                    pen = consumer_tariffs["T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["T_v"]["prispevek_ove"]
                else:
                    sp_obr_moc = consumer_tariffs["not_T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["not_T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["not_T_v"]["omrez_MT"]
                    pen = consumer_tariffs["not_T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["not_T_v"][
                        "prispevek_ove"]

            omr_moc_P = sp_obr_moc * obr_P
            prevec_P = obr_P - self.consumer.PrikljucnaMoc
            if prevec_P > 0:
                cena_pen = prevec_P * pen
            else:
                cena_pen = 0

            omr_VT = obr_VT * omrez_VT
            omr_MT = obr_MT * omrez_MT
            omr_ET = 0

            # ENERGIJA
            obr_ET = es.sum()
            if obr_ET < 20000:
                e_cena = consumer_tariffs["energija"]["20000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["20000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000"]["trosarina"]
            elif obr_ET < 500000:
                e_cena = consumer_tariffs["energija"]["500000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["500000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["500000"]["trosarina"]
            elif obr_ET < 2000000:
                e_cena = consumer_tariffs["energija"]["2000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["2000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["2000000"][
                    "trosarina"]
            elif obr_ET < 20000000:
                e_cena = consumer_tariffs["energija"]["20000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["20000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["20000000"][
                    "trosarina"]
            elif obr_ET < 70000000:
                e_cena = consumer_tariffs["energija"]["70000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["70000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["70000000"][
                    "trosarina"]
            elif obr_ET < 150000000:
                e_cena = consumer_tariffs["energija"]["150000000"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["150000000"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["150000000"][
                    "trosarina"]
            else:
                e_cena = consumer_tariffs["energija"]["ostalo"]["e_cena"]
                dajatve = consumer_tariffs["energija"]["ostalo"]["dajatve"]
                trosarina = consumer_tariffs["energija"]["ostalo"]["trosarina"]
            e_VT = (obr_VT / 1000) * e_cena
            e_MT = (obr_MT / 1000) * e_cena
            e_ET = (obr_ET / 1000) * e_cena

            #TMP
            self.ove_spte_tmp["old_odj4"].append(
                (self.consumer.obracunska_moc, prispevek_ove))

            # OVE
            ove_spte_p = self.consumer.obracunska_moc * prispevek_ove
            ove_spte_e = (dajatve + trosarina) * (obr_ET / 1000)

            return (e_MT, e_VT,
                    e_ET), (omr_moc_P, omr_MT, omr_VT, omr_ET,
                            cena_pen), ove_spte_e, ove_spte_p, omr_wqex

        elif odjID == 3:  # ODJEM NA NN Z MERJENJEM MOČI
            zbiralke = self.consumer.zbiralke
            T_v = self.consumer.ObratovalneUre >= 2500
            obr_P = settlement_power(dates, Ps)

            # OMREZNINA
            if zbiralke:
                if T_v:
                    sp_obr_moc = consumer_tariffs["T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["T_v"]["omrez_MT"]
                    pen = consumer_tariffs["T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["T_v"]["prispevek_ove"]
                else:
                    sp_obr_moc = consumer_tariffs["not_T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["not_T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["not_T_v"]["omrez_MT"]
                    pen = consumer_tariffs["not_T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["not_T_v"][
                        "prispevek_ove"]
            else:
                if T_v:
                    sp_obr_moc = consumer_tariffs["T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["T_v"]["omrez_MT"]
                    pen = consumer_tariffs["T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["T_v"]["prispevek_ove"]
                else:
                    sp_obr_moc = consumer_tariffs["not_T_v"]["sp_obr_moc"]
                    omrez_VT = consumer_tariffs["not_T_v"]["omrez_VT"]
                    omrez_MT = consumer_tariffs["not_T_v"]["omrez_MT"]
                    pen = consumer_tariffs["not_T_v"]["pen"]
                    prispevek_ove = consumer_tariffs["not_T_v"][
                        "prispevek_ove"]

            omr_moc_P = sp_obr_moc * obr_P
            prevec_P = obr_P - self.consumer.PrikljucnaMoc
            if prevec_P > 0:
                cena_pen = prevec_P * pen
            else:
                cena_pen = 0

            omr_VT = obr_VT * omrez_VT
            omr_MT = obr_MT * omrez_MT
            omr_ET = 0.

            # ENERGIJA
            e_VT = obr_VT * consumer_tariffs["energija"]["energ_VT"]
            e_MT = obr_MT * consumer_tariffs["energija"]["energ_MT"]
            e_ET = obr_ET * consumer_tariffs["energija"]["energ_ET"]

            # OVE
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]

            #TMP
            self.ove_spte_tmp["old_odj3"].append(
                (self.consumer.obracunska_moc, prispevek_ove))

            ove_spte_p = self.consumer.obracunska_moc * prispevek_ove
            if self.consumer.samooskrba:  # preveriti če je ok
                ove_spte_e = (delovanje_operaterja + trosarina) * obr_ET
            else:
                ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_ET

            return (e_MT, e_VT,
                    e_ET), (omr_moc_P, omr_MT, omr_VT, omr_ET,
                            cena_pen), ove_spte_e, ove_spte_p, omr_wqex

        elif odjID == 2:  # ODJEM NA NN BREZ MERJENE MOČI    # mali poslovni odjemalci
            obr_P = settlement_power(dates, Ps)  # obračunska moč (W)

            # OMREZNINA
            prevec_P = obr_P - self.consumer.PrikljucnaMoc
            if prevec_P > 0:
                cena_pen = prevec_P * pen
            else:
                cena_pen = 0

            omr_VT = obr_VT * consumer_tariffs["omrez_VT"]
            omr_MT = obr_MT * consumer_tariffs["omrez_MT"]
            omr_ET = obr_ET * consumer_tariffs["omrez_ET"]
            omr_moc_P = self.consumer.obracunska_moc * \
                consumer_tariffs["sp_obr_moc"]

            # ENERGIJA
            e_VT = obr_VT * consumer_tariffs["energija"]["energ_VT"]
            e_MT = obr_MT * consumer_tariffs["energija"]["energ_MT"]
            e_ET = obr_ET * consumer_tariffs["energija"]["energ_ET"]

            # OVE
            prispevek_ove = consumer_tariffs["dajatve"]["prispevek_ove"]
            delovanje_operaterja = consumer_tariffs["dajatve"][
                "delovanje_operaterja"]
            energ_ucinkovitost = consumer_tariffs["dajatve"][
                "energ_ucinkovitost"]
            trosarina = consumer_tariffs["dajatve"]["trosarina"]

            self.ove_spte_tmp["old_odj2"].append(self.consumer.obracunska_moc,
                                                 prispevek_ove)
            ove_spte_p = self.consumer.obracunska_moc * prispevek_ove
            if self.consumer.samooskrba:  # preveriti če je ok
                ove_spte_e = (delovanje_operaterja + trosarina) * obr_ET
            else:
                ove_spte_e = (delovanje_operaterja + energ_ucinkovitost +
                              trosarina) * obr_ET

            return (e_MT, e_VT,
                    e_ET), (omr_moc_P, omr_MT, omr_VT, omr_ET,
                            cena_pen), ove_spte_e, ove_spte_p, omr_wqex
        else:
            return (0, 0, 0), (0, 0, 0, 0, 0), 0, 0, 0

    def calculation_of_tec_penalty(self,
                                   dates,
                                   com_production,
                                   tec_index=None):
        """
        Function calculates the price penalty due to the TEC parameters
        """
        if tec_index is not None:
            consumer_tec_index = tec_index
        else:
            try:
                consumer_tec_index = self.consumer.tec_index
            except:
                raise Exception("TEC index is not defined!")
        consumer_tariffs = self.consumer.constants

        tariff_mask = individual_tariff_times(dates)  # 5×N array
        tec_block_prices = consumer_tariffs["tec"][consumer_tec_index]

        omr_com_production_masked = tariff_mask * com_production

        # calculate the penalty
        obr_tec = omr_com_production_masked * tec_block_prices
        tec_penalty = obr_tec.sum()
        return tec_penalty

    def reset_output(self):
        """
        the function resets the output.
        """
        self._output = {
            "month_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "year": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_MT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_VT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "e_ET": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_moc": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_MT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_VT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_ET": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_jal": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "omr_jal": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_omr_moc": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_omr_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "new_Pens": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "ove_spte_e": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "ove_spte_p": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "obracunske_moci": [0, 0, 0, 0, 0],
            "prikljucna_moc": 0,
            "obracunska_moc": 0,
            "vrsta_odjema": "",
            "postavke": dict(),
            "stevilo_faz": 0,
            "stevilo_tarif": 0,
            "samooskrba": 0,
            "ERROR": 0
        }


if __name__ == "__main__":

    # read data
    path = r"data/6-80061-15minMeritve2023-01-01-2023-12-31.csv"
    data = read_moj_elektro_csv(path)
    tech_data = {
        "blocks": [0, 0, 0, 0, 0],
        "prikljucna_moc": "14 kW (3x20 A)",
        "user_id": 1,
        "samooskrba": 1,
        "zbiralke": 0,
        "trenutno_stevilo_tarif": 2,
        "stevilo_faz": 3
    }
    # 1 - gospodinjski odjem (us0)
    # 2 - odjem na nn brez merjene moči (us0, us1)
    # 3 - odjem na nn z merjeno močjo (us0, us1)
    # 4 - Odjem na SN (us2, us3)
    # 6 - Polnjenje EV
    mapping = {  # priključna moč, obracunska moč
        "4 kW (1x16 A)": [4, 3],
        "5 kW (1x20 A)": [5, 3],
        "6 kW (1x25 A)": [6, 6],
        "7 kW (1x32 A)": [7, 7],
        "8 kW (1x35 A)": [8, 7],
        "11 kW (3x16 A)": [11, 7],
        "14 kW (3x20 A)": [14, 7],
        "17 kW (3x25 A)": [17, 10],
        "22 kW (3x32 A)": [22, 22],
        "24 kW (3x35 A)": [24, 24],
        "28 kW (3x40 A)": [28, 28],
        "35 kW (3x50 A)": [35, 35],
        "43 kW (3x63 A)": [43, 43],
        "55 kW (3x80 A)": [55, 55],
        "69 kW (3x100 A)": [69, 69],
        "86 kW (3x125 A)": [86, 86],
        "110 kW (3x160 A)": [110, 110],
        "138 kW (3x200 A)": [138, 138],
        "drugo": [0, 0]
    }
    tech_data["obracunska_moc"] = mapping[tech_data["prikljucna_moc"]][1]
    tech_data["prikljucna_moc"] = mapping[tech_data["prikljucna_moc"]][0]
    settlement = Settlement()

    settlement.calculate_settlement(0, data, tech_data)
    print(settlement.output)
