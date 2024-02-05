from dash import html, dash_table, Input, Output, State, callback

import base64
import datetime
import io
import pandas as pd

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
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
    elif "PodatkiMM" in filename:
        # df.rename
        mm_data = df.iloc[0]
        tech_data = {
            "blocks": [0, 0, 0, 0, 0],
            "prikljucna_moc": mm_data["Priključna moč odjema po SzP"],
            "consumer_type_id": 1,
            "samooskrba": 0,
            "zbiralke": 0,
            "trenutno_stevilo_tarif": 2,
            "stevilo_faz": mm_data["Število faz"],
        }

        # tech_data["stevilo_faz"] = mapping[tech_data["prikljucna_moc"]][2]
        # tech_data["obracunska_moc"] = mm_data["Vrednost obračunske moči"]
        # tech_data["prikljucna_moc"] = mapping[tech_data["prikljucna_moc"]][0]
    return (filename, df)


    # return html.Div([
    #     html.H5(filename),
    #     html.H6(datetime.datetime.fromtimestamp(date)),

    #     dash_table.DataTable(
    #         df.to_dict('records'),
    #         [{'name': i, 'id': i} for i in df.columns]
    #     ),

    #     html.Hr(),  # horizontal line

    #     # For debugging, display the raw contents provided by the web browser
    #     html.Div('Raw Content'),
    #     html.Pre(contents[0:200] + '...', style={
    #         'whiteSpace': 'pre-wrap',
    #         'wordBreak': 'break-all'
    #     })
    # ])