import json

import pandas as pd

from constants import constants
from utils import *


class Consumer(object):

    def __init__(self, smm: int) -> None:
        self._smm_consumption = None
        self._smm_tech_data = None
        self.part_of_community = False
        self._koo_times = None
        self._constants = None

        self.__dates = None
        self._powers = None

    @property
    def smm(self) -> int:
        return self._smm

    @property
    def smm_consumption(self) -> pd.DataFrame:
        return self._smm_consumption

    @property
    def smm_tech_data(self) -> pd.DataFrame:
        return self._smm_tech_data

    @property
    def dates(self) -> np.array:
        return self.__dates

    @property
    def powers(self) -> np.array:
        return self._powers

    @property
    def constants(self) -> pd.DataFrame:
        return self._constants

    @property
    def koo_times(self) -> dict:
        return self._koo_times

    @smm.setter
    def smm(self, value):
        self._smm = value

    @smm_consumption.setter
    def smm_consumption(self, value):
        self._smm_consumption = value

    @smm_tech_data.setter
    def smm_tech_data(self, value):
        self._smm_tech_data = value

    @dates.setter
    def dates(self, value):
        self.__dates = value

    @powers.setter
    def powers(self, value):
        self._powers = value

    @constants.setter
    def constants(self, value):
        self._constants = value

    @koo_times.setter
    def koo_times(self, value):
        self._koo_times = value

    def __repr__(self) -> str:
        return "<DataHandler(smm: int, con: pyodbc.connction)>"

    def __str__(self) -> str:
        return "<DataHandler(smartmeter id, db-connection)>"

    def load_consumer_data(self,
                           timeseries_data=None,
                           tech_data=None,
                           preprocess=True,
                           calculate_obr_p_values=False,
                           override_year=False):
        """
        Function load_data loads the data from 'start' to 'end' date.

        INPUT::
        :param start: Start year-date in a form "2021-01-01"
        :param end: End year-date in a form "2022-01-01"

        OUTPUT::
        :return: None
        """

        # Load and preprocess the consumer data
        self.load_and_handle_data_manually(
            timeseries_data,
            tech_data,
            preprocess=preprocess,
            calculate_obr_p_values=calculate_obr_p_values,
            override_year=override_year)

    def load_and_handle_data_manually(self,
                                      df: pd.DataFrame = False,
                                      tech_data: json = False,
                                      preprocess=True,
                                      calculate_obr_p_values=False,
                                      override_year=False):
        """
            Function get_data gets the data from 'start' to 'end' date.
                Function populated the self.smm_consumption and self.smm_tech_data properties.

                INPUT: start    ... Start year-date in a form "2021-01-01"
                                end     ... End year-date in a form "2022-01-01"
                OUTPUT: None
        """
        self.connected_power = tech_data["prikljucna_moc"]
        self.billing_power = tech_data["obracunska_moc"]
        self.num_tariffs = tech_data["stevilo_tarif"]
        self.num_phases = tech_data["stevilo_faz"]
        self.samooskrba = tech_data["samooskrba"]
        self.bus_bar = tech_data["zbiralke"]
        self.operating_hours = tech_data["obratovalne_ure"]
        self.consumer_type_id = tech_data["consumer_type_id"]
        self.consumer_type = tech_data["uporabniska_skupina"]

        if preprocess:
            df = self.preprocess(df)

        self.smm_consumption = df
        # extract the dates and the Ps values for calculations of the settlement
        self.dates = df.index
        self.powers = df.p.values

        if any(x is None for x in tech_data["obr_p_values"]):
            calculate_obr_p_values = True

        if calculate_obr_p_values:
            self.new_billing_powers = self.find_new_billing_powers()
        else:
            self.new_billing_powers = np.array(tech_data["obr_p_values"])

        if override_year:
            year = 2024
        else:
            year = self.dates[0].year

        if self.bus_bar:
            self.constants = constants[str(year)][
                self.consumer_type_id]["zbiralke"]
        else:
            self.constants = constants[str(year)][
                self.consumer_type_id]["not_zbiralke"]
        if self.consumer_type_id > 2:
            self.koo_times = constants[str(year)]["koo_times"]
        else:
            self.koo_times = None

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
                Function preprocessed the input dataframe and outputs a preprocessed dataframe

                INPUT: df                   ... raw pandas dataframe from the query in self.data_loader object
                OUTPUT: df_preprocessed     ... preprocessed pandas dataframe
        """

        df_preprocessed = df.copy()

        df_preprocessed = df_preprocessed[df_preprocessed.p < (
            2 * float(self.connected_power))]
        # df_preprocessed = df_preprocessed[df_preprocessed.p < -float(prikljucna_moc_oddaja)]
        if df_preprocessed.shape[0] != 35040:
            df_preprocessed.drop_duplicates(subset="datetime", inplace=True)
            df_preprocessed.datetime = pd.to_datetime(df_preprocessed.datetime)
            df_preprocessed = df_preprocessed.set_index("datetime")
            # fill nan values with 0
            df_preprocessed = df_preprocessed.resample("15min").interpolate()
            # fill nan values with mean
            # df_preprocessed = df_preprocessed.fillna(df_preprocessed.mean())
        else:
            df_preprocessed.datetime = pd.to_datetime(df_preprocessed.datetime)
            df_preprocessed = df_preprocessed.set_index("datetime")
        return df_preprocessed

    def find_new_billing_powers(self, find_optimal=False) -> np.array:
        self.tariff_mask = individual_tariff_times(self.dates)
        masked_powers = self.powers * self.tariff_mask
        min_obr_power = find_min_obr_p(int(self.num_phases),
                                       int(self.connected_power))
        obr_p_values = [0, 0, 0, 0, 0]
        for i in range(5):
            if not find_optimal:
                if self.connected_power <= 43:
                    obr_power = np.average(np.sort(masked_powers[i])[-3:])
                else:
                    obr_power = np.amax(masked_powers[i])
            else:
                idx_months = month_indexes(self.dates)
                obr_power = find_optimal_block_settlement_power(
                    masked_powers[i], i, idx_months)
            if min_obr_power > obr_power:
                obr_p_values[i] = min_obr_power
            else:
                obr_p_values[i] = obr_power
        current_max = obr_p_values[0]
        for i in range(5):
            if obr_p_values[i] < current_max:
                obr_p_values[i] = current_max
            else:
                current_max = obr_p_values[i]
        return np.array(obr_p_values)
