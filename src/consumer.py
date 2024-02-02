import json
import pandas as pd

from constants import constants
from utils import *


class Consumer(object):

    def __init__(self, smm: int) -> None:
        self._smm_consumption = None
        self._smm_tech_data = None
        self.part_of_community = False
        self._constants = None

        # JSON Data
        self.samooskrba = False
        self.zbiralke = None
        self.consumer_type_id = None
        self.stevilo_faz = None
        self.prikljucna_moc = None

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

    def __repr__(self) -> str:
        return "<DataHandler(smm: int, con: pyodbc.connction)>"

    def __str__(self) -> str:
        return "<DataHandler(smartmeter id, db-connection)>"

    def load_consumer_data(self,
                           timeseries_data=None,
                           tech_data=None,
                           preprocess=True):
        """
        Function load_data loads the data from 'start' to 'end' date.

        INPUT::
        :param start: Start year-date in a form "2021-01-01"
        :param end: End year-date in a form "2022-01-01"

        OUTPUT::
        :return: None
        """

        # Load and preprocess the consumer data
        self.load_and_handle_data_manually(timeseries_data,
                                           tech_data,
                                           preprocess=preprocess)
        # Finding block settlement tariffs
        self.new_billing_powers = self.find_obr_powers()

    def load_and_handle_data_manually(
        self,
        df: pd.DataFrame = False,
        tech_data: json = False,
        preprocess=True,
    ):
        """
            Function get_data gets the data from 'start' to 'end' date.
                Function populated the self.smm_consumption and self.smm_tech_data properties.

                INPUT: start    ... Start year-date in a form "2021-01-01"
                                end     ... End year-date in a form "2022-01-01"
                OUTPUT: None
        """

        tmp_smm_consumption = df
        self.connected_power = tech_data["prikljucna_moc"]
        self.billing_power = tech_data["obracunska_moc"]
        self.num_tariffs = tech_data["trenutno_stevilo_tarif"]
        self.num_phases = tech_data["stevilo_faz"]
        self.samooskrba = tech_data["samooskrba"]
        self.bus_bar = tech_data["zbiralke"]
        self.consumer_type_id = tech_data["consumer_type_id"]

        self.year = tmp_smm_consumption.datetime[0].year
        if self.zbiralke == "zbiralke":
            self.constants = constants[str(
                self.year)][self.consumer_type_id]["zbiralke"]
        else:
            self.constants = constants[str(
                self.year)][self.consumer_type_id]["not_zbiralke"]

        if preprocess:
            tmp_smm_consumption = self.preprocess(tmp_smm_consumption)

        self.smm_consumption = tmp_smm_consumption
        # extract the dates and the Ps values for calculations of the settlement
        self.dates = tmp_smm_consumption.index
        self.powers = tmp_smm_consumption.p.values

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
                Function preprocessed the input dataframe and outputs a preprocessed dataframe

                INPUT: df                   ... raw pandas dataframe from the query in self.data_loader object
                OUTPUT: df_preprocessed     ... preprocessed pandas dataframe
        """

        df_preprocessed = df.copy()

        df_preprocessed = df_preprocessed[df_preprocessed.p < (
            1.3 * float(self.connected_power))]
        # df_preprocessed = df_preprocessed[df_preprocessed.p < -float(prikljucna_moc_oddaja)]
        if df_preprocessed.shape[0] != 35040:
            df_preprocessed.drop_duplicates(subset="datetime", inplace=True)
            df_preprocessed.datetime = pd.to_datetime(df_preprocessed.datetime)
            df_preprocessed = df_preprocessed.set_index("datetime")
            # fill nan values with 0
            df_preprocessed = df_preprocessed.resample("15min").asfreq()
            # fill nan values with mean
            df_preprocessed = df_preprocessed.fillna(df_preprocessed.mean())
        else:
            df_preprocessed.datetime = pd.to_datetime(df_preprocessed.datetime)
            df_preprocessed = df_preprocessed.set_index("datetime")
        return df_preprocessed

    def find_obr_powers(self) -> np.array:
        self.tariff_mask = individual_tariff_times(self.dates)
        Ps_masked = self.powers * self.tariff_mask
        min_P_obr = find_min_obr_p(int(self.num_phases), int(self.connected_power))
        obr_blocks = [0, 0, 0, 0, 0]
        for i in range(5):
            # OPTIMISATION: Possibly 3x calculate max
            obr_P = np.average(np.sort(Ps_masked[i])[-3:])
            if min_P_obr > obr_P:
                obr_blocks[i] = min_P_obr
            else:
                obr_blocks[i] = obr_P
        current_max = obr_blocks[0]
        for i in range(5):
            if obr_blocks[i] < current_max:
                obr_blocks[i] = current_max
            else:
                current_max = obr_blocks[i]
        return np.array(obr_blocks)
