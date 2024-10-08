import pandas as pd
import numpy as np
import holidays
import datetime
import warnings
warnings.filterwarnings("ignore")



def energija_omreznine(df, bloki_cene_energije, placilo_omr_e):
    cene_e = placilo_omr_e
    df_energy = df.loc[df.a > 0]
    df_energy = df_energy[["a", "year_month", "block"]].groupby(["year_month", "block"]).sum()
    for year_month, vals in df_energy.groupby(level=0):
        _, month = year_month.split("-")
        df = vals.droplevel(0)
        # df = vals
        for i in range(1, 6):
            if i not in df.index:
                # insert it at the beginning
                df.loc[i] = 0
        cena = df["a"] * bloki_cene_energije
        cene_e[int(month) - 1] = cena.sum()
    cene_e = np.array(cene_e)
    return cene_e

def moc_omreznine(df, bloki, bloki_cene_moci, placilo_omr_p):
    placilo_p = placilo_omr_p
    power = df[["p", "year_month", "block"]].groupby(["year_month", "block"]).max()
    for year_month, _ in power.groupby(level=0):
        _, month = year_month.split("-")
        if int(month) in [1,2,11,12]:
            cena = bloki * bloki_cene_moci * [1, 1, 1, 1, 0]
        else:
            cena = bloki * bloki_cene_moci * [0, 1, 1, 1, 1]
        placilo_p[int(month) - 1] = cena.sum()

    placilo_p = np.array(placilo_p)
    return placilo_p

from utils import handle_obr_moc, find_min_obr_p

def predlagane_obr_moci(df, prikljucna_moc, st_faz, skupina_koncnih_odjemalcev):
    blocks = []
    for block in range(1, 6):
        if skupina_koncnih_odjemalcev <= 1:
            selected_season = df[df.month.isin([1,2,11,12])]
            block_value = np.average(selected_season.loc[selected_season.block == block, "p"].nlargest(3))
        else:
            block_value = np.average(df.loc[df.block == block, "p"].nlargest(1))
        blocks.append(block_value)
    min_obr_p = find_min_obr_p(st_faz, prikljucna_moc)
    blocks = np.array(handle_obr_moc(blocks, prikljucna_moc, min_obr_p))
    # round
    blocks = np.round(blocks, 1)
    return blocks

def penali(df, bloki, Fex, placilo_omr_penali):
    cene_penali = placilo_omr_penali
    df["block_max_power"] = df["block"].apply(lambda x: bloki[x-1] if x < len(bloki) else None)

    # subtract the block_max_power from actual power p and only take positive values.
    diff = df["p"] - df["block_max_power"]
    df["power_exceeded"] = diff * (diff > 0)
    df = df[["year_month", "block", "power_exceeded"]]
    df_penali = df.groupby(["block", "year_month"]).sum()

    for _, vals in df_penali.groupby(level=0):
        df = vals.droplevel(1)
        cena = Fex * np.sqrt(sum(df["power_exceeded"]**2))
        block = df.index[0]
        cene_penali[block - 1] = cena
    cene_penali = np.array(cene_penali)
    return cene_penali


def individual_tariff_times(dates: np.array) -> np.array:
    """
    Generates block assignments (1-5) for the given dates.

    Takes an array of dates and returns an array of block assignments (1-5).

    Args:
    ----------
        dates: np.array
            Array of dates in format of Pandas datetime

    Returns:
    ----------
        block_assignments: np.array
            Array where each entry corresponds to the block number (1-5) for the given date.
    """
    # Prepare array of holidays
    si_holidays = holidays.SI(years=(dates.iloc[0].year, dates.iloc[-1].year))

    # Tariff block values (obr_p_values table)
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

    # Combine the seasons
    high_season = [high_season_working, high_season_workoff]
    low_season = [low_season_working, low_season_workoff]
    obr_p_values = [low_season, high_season]

    # Initialize array for block assignments
    block_assignments = np.zeros(len(dates), dtype=int)

    # Loop through dates to assign blocks
    for i, date in enumerate(dates):
        # Adjust for 15 minutes earlier (tariff is for the previous quarter-hour)
        date -= datetime.timedelta(minutes=15)

        # Determine if it's a holiday or weekend
        workoff = 1 if date in si_holidays or date.weekday() > 4 else 0

        # Determine if it's high season (November to February)
        high_season_flag = 1 if date.month in [1, 2, 11, 12] else 0

        # Get the hour
        hour = date.hour

        # Determine the block (subtract 1 for 0-based indexing)
        block = obr_p_values[high_season_flag][workoff][hour]

        # Assign the block number to the output array
        block_assignments[i] = block

    return block_assignments

def handle_obr_moc(predlagane_obracunske_moci, prikljucna_moc, min_obr_p):
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
        # check if any of the values is higher than the connected power
        for i in range(len(predlagane_obracunske_moci)):
            if predlagane_obracunske_moci[i] > prikljucna_moc:
                predlagane_obracunske_moci[i] = prikljucna_moc

        return predlagane_obracunske_moci


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

def prepare_dataframe(df: pd.DataFrame):
    """
    Function prepares the dataframe and adds the parameters for the calculation of the omreznina
    """
    df["date_time"] = pd.to_datetime(df["date_time"])
    df["block"] = individual_tariff_times(df["date_time"])
    df["month"] = df["date_time"].dt.month
    df["year"] = df["date_time"].dt.year
    # create a year_month column that combines year and month with a -
    df["year_month"] = df["year"].astype(str) + "-" + df["month"].astype(str)
    return df

def calculate_omreznina(df: pd.DataFrame, args):
    """
    Function calculates the omreznina.

    Parameters:
    -----------
    df: pd.DataFrame
        The dataframe that contains the follwoing parameters:
              | date_time | p |
              |     x     | x |
    """
    df = prepare_dataframe(df)
    placilo_omr_e = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    placilo_omr_p = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    placilo_omr_penali = [0, 0, 0, 0, 0]
    if args["net_metering"]:
        if df.a.sum() < 0:
            placilo_omr_e = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        else:
            placilo_omr_e = energija_omreznine(df, args["bloki_cene_energije"], placilo_omr_e)
    else:
        placilo_omr_e = energija_omreznine(df, args["bloki_cene_energije"], placilo_omr_e)

    bloki = predlagane_obr_moci(df, args["prikljucna_moc"], args["st_faz"], args["skupina_koncnih_odjemalcev"])
    placilo_omr_p = moc_omreznine(df, bloki, args["bloki_cene_moci"], placilo_omr_p)
    placilo_omr_penali = penali(df, bloki, args["Fex"], placilo_omr_penali)

    return placilo_omr_e, placilo_omr_p, placilo_omr_penali