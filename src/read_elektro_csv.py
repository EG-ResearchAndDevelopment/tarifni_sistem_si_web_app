import pandas as pd


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

    print(df)
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
