from dash import html, dash_table, Input, Output, State, callback

import base64
import datetime
import io
import pandas as pd


def parse_contents(contents, filename):
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    
    if "15minMeritve" in filename:
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

    else:
        return None
    return (filename, df)
