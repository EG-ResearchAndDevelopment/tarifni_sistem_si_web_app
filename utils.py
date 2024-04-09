import datetime
import datetime as dt
import functools

import holidays
import numpy as np
import pandas as pd
from scipy import optimize

from constants import constants


###############################################################
#															  #
################### OLD SYSTEM UTILITY ########################
#															  #
###############################################################
def construct_high_tariff_time_mask(dates: np.array) -> np.array:
    """
	Function returns a mask of 1 and 0, 1 means that it is within high tariff time.
	High tariff time is from 6:00 to 22:00 except on holidays and weekends.

		INPUT: dates - numpy array of dates
		OUTPUT: mask - numpy array mask of 1 and 0 of the same length as dates
	"""
    ht_mask = np.zeros(len(dates))
    # get holidays in Slovenia for the year from library holidays
    hd = holidays.SI(years=int(dates[0].year))
    for i in range(len(dates) - 1):
        date = dates[i]
        hour = date.hour
        if date.weekday() < 5:  # weekdays
            if date.date() not in hd:  # not a holiday
                if hour >= 6 and hour < 22:  # high tariff time
                    ht_mask[
                        i +
                        1] = 1  # mask is shifted by 1 because of the way the data is loaded
    return ht_mask


def construct_koo_mask(dates: np.array, koo_times) -> np.array:
    """
	Function returns a mask of 1 and 0, 1 means that it is within KOO time.
	KOO times are stored in constants and are year, month and hour dependent.

		INPUT: dates - numpy array of dates
		OUTPUT: mask - numpy array mask of 1 and 0 of the same length as dates
	"""

    koo_mask = np.zeros(len(dates), dtype=int)
    for i, date in enumerate(dates):
        month = date.month
        time = date.time()

        start_hour, end_hour = koo_times[month]

        if start_hour < time <= end_hour:
            koo_mask[i] = 1
    return koo_mask


###############################################################
#															  #
################### NEW SYSTEM UTILITY ########################
#															  #
###############################################################


def settlement_power(dates: np.array,
                     powers: np.array,
                     koo_times: np.array = None) -> float:
    """
	Function calculates the settlement power (obracunska moc) for the given dates and power consumption.
	Balance power is the average of the highest 3 power consumption values in the KOO time and
	the average of the highest 3 power consumption values in the non-KOO time.

		INPUT: dates - numpy array of dates
				Ps - numpy array of power consumption
		OUTPUT: P_obr - settlement power
	"""
    # if koo_times are not given
    # construct high tariff time mask (VT mask)
    if koo_times == None:
        # print("using high tariff time mask")
        mask = construct_high_tariff_time_mask(dates)
    # else conctruct koo_mask
    else:
        # print("using koo mask")
        mask = construct_koo_mask(dates, koo_times)

    masked_powers = mask * powers
    inverse_masked_powers = powers * (mask - 1) * -1
    inverse_masked_obr_p = np.average(
        inverse_masked_powers[inverse_masked_powers.argsort()][-3:]) * 0.25
    masked_obr_p = np.average(masked_powers[masked_powers.argsort()][-3:])
    if masked_obr_p > inverse_masked_obr_p:
        return masked_obr_p
    else:
        return inverse_masked_obr_p


def individual_tariff_times(dates: np.array) -> np.array:
    """
	Generates tariff masks for the given dates

    Takes an array of dates and returns a matrix of 5 tariff masks from block 1 to 5.
    Each mask is a vector of 1 and 0. 1 means that the time datetime falls into the block.

	Args:
	----------
		dates: np.array
            Array of dates

	Returns:
	----------
		tariff_mask: np.array
			Tariff mask
	"""
    # Prepare array of holidays
    si_holidays = holidays.SI(years=(dates[0].year, dates[-1].year))

    # Tariff obr_p_values table http://www.pisrs.si/Pis.web/npb/2024-01-0154-2022-01-3624-npb5-p2.pdf
    high_season_working = [
        3, 3, 3, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 3, 3
    ]
    low_season_working = [
        4, 4, 4, 4, 4, 4, 3, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 3, 3, 4, 4
    ]
    high_season_workoff = [
        4, 4, 4, 4, 4, 4, 3, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2, 2, 2, 2, 3, 3, 4, 4
    ]
    low_season_workoff = [
        5, 5, 5, 5, 5, 5, 4, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 3, 3, 4, 4, 5, 5
    ]

    # combine obr_p_values into two seasons
    high_season = [high_season_working, high_season_workoff]
    low_season = [low_season_working, low_season_workoff]

    # combine both seasons
    obr_p_values = [low_season, high_season]

    # np.array([block_1, block_2, block_3, block_4, block_5])
    tariff_mask = np.zeros((5, len(dates)), dtype=int)

    i = 0
    for date in dates:
        date -= datetime.timedelta(minutes=15)
        if date in si_holidays or date.weekday() > 4:
            workoff = 1
        else:
            workoff = 0

        if date.month in [1, 2, 11, 12]:
            high_season = 1
        else:
            high_season = 0

        hour = date.hour
        # takes the correct block and subtracts 1 because array indexing starts at 0
        j = obr_p_values[high_season][workoff][hour] - 1
        tariff_mask[j][i] = 1

        i += 1

    return tariff_mask


def month_indexes(dates: np.array) -> np.array:
    """
	Function returns the indexes of the first day of each month in the given dates array.

		INPUT: dates - numpy array of dates (must be sorted)
		OUTPUT: inds - numpy array of indexes
	"""
    inds = [0]
    m = 1
    for i in range(len(dates)):
        d = dates[i]
        if m - d.month != 0:
            inds.append(i + 1)
            m = d.month
    inds.append(len(dates) - 1)
    return inds


def find_min_obr_p(n_phases: int, connected_power: int) -> float:
    if connected_power > 43:
        return 0.25 * connected_power
    elif connected_power <= 43 and n_phases == 1:
        if 0.31 * connected_power > 2:
            return 0.31 * connected_power
        else:
            return 2
    elif connected_power <= 17 and n_phases == 3:
        if 0.27 * connected_power > 3.5:
            return 0.27 * connected_power
        else:
            return 3.5
    elif connected_power <= 43 and connected_power > 17 and n_phases == 3:
        if 0.34 * connected_power > 3.5:
            return 0.34 * connected_power
        else:
            return 3.5
    else:
        # produce a warning
        print(
            "Warning: it is not possible to calculate the minimum proposed settlement power."
        )
        return 0.


def read_moj_elektro_csv(
        path: str = '../data/input_data/moj_elektro.csv') -> pd.DataFrame:
    """Reads and preprocesses moj elektro csv and returns pandas dataframe.
    
    Args:
    ----------
        path: str
            Path to csv file
            
    Returns:
    ----------
        df: pd.DataFrame
            Timeseries data for the given year
            
    """
    df = pd.read_excel(path, sheet_name="6-123604")
    # df = pd.read_csv(path, sep=",", decimal=".")

    df.rename(columns={'Časovna značka': 'datetime'}, inplace=True)
    # fill nan with 0
    df = df.fillna(0)
    # convert datetime to to CET
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Calculate net active and reactive power
    df['p'] = df['P+ Prejeta delovna moč'] - df['P- Oddana delovna moč']
    df['q'] = df['Q+ Prejeta jalova moč'] - df['Q- Oddana jalova moč']
    df['a'] = df['Energija A+'] - df['Energija A-']
    df['r'] = df['Energija R+'] - df['Energija R-']

    # drop columns
    df = df[['datetime', 'p', 'q', 'a', 'r']]
    # drop duplicates
    df = df.drop_duplicates(subset='datetime', keep='first')
    df["datetime"] = pd.to_datetime(df.datetime)
    df.set_index('datetime', inplace=True, drop=True)
    df.sort_index(inplace=True)

    # # resample
    df = df.resample('15min').mean()

    df.reset_index(inplace=True)

    return df


def handle_prikljucna_moc(predlagane_obracunske_moci, min_obr_p):
    if predlagane_obracunske_moci[0] is None:
        return [min_obr_p, min_obr_p, min_obr_p, min_obr_p, min_obr_p]
    else:
        lowest = predlagane_obracunske_moci[0]
        if lowest < min_obr_p:
            predlagane_obracunske_moci[0] = min_obr_p
        for i in range(1, len(predlagane_obracunske_moci)):
            if predlagane_obracunske_moci[i] < lowest:
                predlagane_obracunske_moci[i] = lowest
            else:
                lowest = predlagane_obracunske_moci[i]
        return predlagane_obracunske_moci
