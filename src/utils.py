import numpy as np
import datetime as dt
import holidays
import functools
from scipy import optimize

from constants import constants


###############################################################
#															  #
################### OLD SYSTEM UTILITY ########################
#															  #
###############################################################
def high_tariff_time(dates: np.array) -> np.array:
    """
	Function returns a mask of 1 and 0, 1 means that it is within high tariff time.
	High tariff time is from 6:00 to 22:00 except on holidays and weekends.

		INPUT: dates - numpy array of dates
		OUTPUT: mask - numpy array mask of 1 and 0 of the same length as dates
	"""
    VT_mask = np.zeros(len(dates))
    # get holidays in Slovenia for the year from library holidays
    hd = holidays.SI(years=int(dates[0].year))
    for i in range(len(dates) - 1):
        date = dates[i]
        hour = date.hour
        if date.weekday() < 5:  # weekdays
            if date.date() not in hd:  # not a holiday
                if hour >= 6 and hour < 22:  # high tariff time
                    VT_mask[
                        i +
                        1] = 1  # mask is shifted by 1 because of the way the data is loaded
    return VT_mask


def KOO_time(dates: np.array) -> np.array:
    """
	Function returns a mask of 1 and 0, 1 means that it is within KOO time.
	KOO times are stored in constants and are year, month and hour dependent.

		INPUT: dates - numpy array of dates
		OUTPUT: mask - numpy array mask of 1 and 0 of the same length as dates
	"""

    KOO = np.zeros(len(dates), dtype=int)
    for i in range(len(dates) - 1):
        date = dates[i]
        date_year = str(date.year)
        date_month = date.month
        date_time = date.time()

        start_hour, end_hour = constants[date_year]["koo_times"][
            date_month].values()

        if start_hour < date_time <= end_hour:
            KOO[i] = 1
    return KOO


###############################################################
#															  #
################### NEW SYSTEM UTILITY ########################
#															  #
###############################################################


def settlement_power(dates: np.array, Ps: np.array) -> float:
    """
	Function calculates the settlement power (obracunska moc) for the given dates and power consumption.
	Balance power is the average of the highest 3 power consumption values in the KOO time and
	the average of the highest 3 power consumption values in the non-KOO time.

		INPUT: dates - numpy array of dates
				Ps - numpy array of power consumption
		OUTPUT: P_obr - settlement power
	"""
    KOO_mask = KOO_time(dates)
    Ps_KOO = KOO_mask * Ps
    Ps_neKOO = Ps * (KOO_mask - 1) * -1
    P_obr_neKOO = np.average(Ps_neKOO[Ps_neKOO.argsort()][-3:]) * 0.25
    P_obr_KOO = np.average(Ps_KOO[Ps_KOO.argsort()][-3:])
    if P_obr_KOO > P_obr_neKOO:
        return P_obr_KOO
    else:
        return P_obr_neKOO


def individual_tariff_times(
    dates: np.array
) -> tuple[np.array, np.array, np.array, np.array, np.array]:
    """
	Function calculates the 5 tariff hours for the given dates.
	Tariff hours are calculated based on the new 5-tariff system.

		INPUT: dates - numpy array of dates
		OUTPUT: u1, u2, u3, u4, u5 - numpy arrays of masks for tariff hours of each tariff
	"""
    u1 = np.zeros(len(dates))
    u2 = np.zeros(len(dates))
    u3 = np.zeros(len(dates))
    u4 = np.zeros(len(dates))
    u5 = np.zeros(len(dates))
    for i in range(len(dates) - 1):
        a = 0
        date = dates[i]
        month = date.month
        hour = date.hour
        if month in [1, 2, 11, 12]:
            a += 1
        if date.weekday() < 5:
            a += 1
        if a == 2:
            if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
                u3[i + 1] = 1
            elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
                u1[i + 1] = 1
            elif (hour == 6) or (hour == 14) or (hour == 15) or (
                    hour == 20) or (hour == 21):
                u2[i + 1] = 1
        elif a == 1:
            if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
                u4[i + 1] = 1
            elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
                u2[i + 1] = 1
            elif (hour == 6) or (hour == 14) or (hour == 15) or (
                    hour == 20) or (hour == 21):
                u3[i + 1] = 1
        elif a == 0:
            if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
                u5[i + 1] = 1
            elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
                u3[i + 1] = 1
            elif (hour == 6) or (hour == 14) or (hour == 15) or (
                    hour == 20) or (hour == 21):
                u4[i + 1] = 1
    date = dates[0]
    month = date.month
    hour = date.hour
    a = 0
    if month in [1, 2, 11, 12]:
        a += 1
    if date.weekday() < 5:
        a += 1
    if a == 2:
        if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
            u3[0] = 1
        elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
            u1[0] = 1
        elif (hour == 6) or (hour == 14) or (hour == 15) or (hour
                                                             == 20) or (hour
                                                                        == 21):
            u2[0] = 1
    elif a == 1:
        if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
            u4[0] = 1
        elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
            u2[0] = 1
        elif (hour == 6) or (hour == 14) or (hour == 15) or (hour
                                                             == 20) or (hour
                                                                        == 21):
            u3[0] = 1
    elif a == 0:
        if (hour >= 0 and hour <= 5) or (hour >= 22 and hour <= 23):
            u5[0] = 1
        elif (hour >= 7 and hour <= 13) or (hour >= 16 and hour <= 19):
            u3[0] = 1
        elif (hour == 6) or (hour == 14) or (hour == 15) or (hour
                                                             == 20) or (hour
                                                                        == 21):
            u4[0] = 1
    return u1, u2, u3, u4, u5


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


def min_obr_P(n_phases: int, connected_power: int) -> float:
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
