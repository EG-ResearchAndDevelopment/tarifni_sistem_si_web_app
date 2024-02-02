import numpy as np
import datetime as dt
import holidays
import functools
from scipy import optimize
import datetime

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


def construct_koo_mask(dates: np.array) -> np.array:
    """
	Function returns a mask of 1 and 0, 1 means that it is within KOO time.
	KOO times are stored in constants and are year, month and hour dependent.

		INPUT: dates - numpy array of dates
		OUTPUT: mask - numpy array mask of 1 and 0 of the same length as dates
	"""

    koo_mask = np.zeros(len(dates), dtype=int)
    for i in range(len(dates) - 1):
        date = dates[i]
        date_year = str(date.year)
        date_month = date.month
        date_time = date.time()

        start_hour, end_hour = constants[date_year]["koo_times"][
            date_month].values()

        if start_hour < date_time <= end_hour:
            koo_mask[i] = 1
    return koo_mask


###############################################################
#															  #
################### NEW SYSTEM UTILITY ########################
#															  #
###############################################################


def settlement_power(dates: np.array, powers: np.array) -> float:
    """
	Function calculates the settlement power (obracunska moc) for the given dates and power consumption.
	Balance power is the average of the highest 3 power consumption values in the KOO time and
	the average of the highest 3 power consumption values in the non-KOO time.

		INPUT: dates - numpy array of dates
				Ps - numpy array of power consumption
		OUTPUT: P_obr - settlement power
	"""
    koo_mask = construct_koo_mask(dates)
    koo_powers = koo_mask * powers
    non_koo_powers = powers * (koo_mask - 1) * -1
    non_koo_obr_p = np.average(
        non_koo_powers[non_koo_powers.argsort()][-3:]) * 0.25
    koo_obr_p = np.average(koo_powers[koo_powers.argsort()][-3:])
    if koo_obr_p > non_koo_obr_p:
        return koo_obr_p
    else:
        return non_koo_obr_p


def individual_tariff_times(
    dates: np.array
) -> np.array([np.array, np.array, np.array, np.array, np.array]):
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

    # Tariff blocks table http://www.pisrs.si/Pis.web/npb/2024-01-0154-2022-01-3624-npb5-p2.pdf
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

    # combine blocks into two seasons
    high_season = [high_season_working, high_season_workoff]
    low_season = [low_season_working, low_season_workoff]

    # combine both seasons
    blocks = [low_season, high_season]

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
        j = blocks[high_season][workoff][hour] - 1
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


def block_power_settlement(Ps: np.array, obr_P: np.array, block: int,
                           idx_months: np.array) -> float:
    """
	Function gets the power consumption of a block and returns the price for the year for the block.

		INPUT: Ps - numpy array of power consumption of the block
			   obr_P - numpy array of the power consumption of the block for the year
			   block - block number
			   idx_months - numpy array of indexes of the first day of each month
		OUTPUT: Pens - price for the penalties for the given powers and the block
	"""
    Pex = (Ps - obr_P) * (Ps > obr_P)
    Pens = functools.reduce(
        lambda acc, val: acc + np.sqrt(
            sum(Pex[idx_months[val[0] - 1]:idx_months[val[0]]]**2)),
        enumerate(idx_months), 0)
    # for i in range(len(idx_months)-1):
    # 	Pens  +=  np.sqrt(sum(Pex[idx_months[i]:idx_months[i+1]]**2))
    if block > 1:
        return 0.9 * Pens + 12 * obr_P  #0.9 = Faktor presežne moči
    else:
        return 0.9 * Pens + 4 * obr_P  #4, ker sta tarifi 1 in 2 veljavni le pozimi


def find_block_settlement_power(Ps: np.array, block: int,
                                idx_months: np.array) -> float:
    """
	Function gets the power consumption of a block and 
	returns the optimal proposed settlement power for the year for the block.

		INPUT: Ps - numpy array of power consumption of the block
			   block - block number
			   idx_months - numpy array of indexes of the first day of each month
		OUTPUT: obr_P - optimal proposed settlement power for the year for the block

	"""
    f = lambda obr_P: block_power_settlement(Ps, obr_P, block + 1, idx_months)
    # optimize.minimize(f, x0=np.amax(Ps)*9/10)
    return optimize.minimize_scalar(f).x


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
