import base64
import calendar
import io

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import html


def create_empty_figure():
    x = [
        'jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt',
        'nov', 'dec'
    ]
    x1 = np.arange(1, calendar.monthrange(2023, 1)[1] + 1, 1)
    y1 = np.random.randint(60, 100, calendar.monthrange(2023, 1)[1])
    y = np.zeros(12)

    fig = go.Figure(data=[
        go.Bar(x=x, y=y, name='Star sistem', marker={'color': '#C32025'})
    ])
    fig.add_trace(
        go.Bar(x=x,
               y=y,
               name='Nov sistem',
               marker={'color': 'rgb(145, 145, 145)'}))

    # fig2 = go.Figure(
    #     data=[go.Bar(x=x1, y=y1, name='2023', marker={'color': '#C32025'})])

    fig.update_layout(
        bargap=0.3,
        transition={
            'duration': 300,
            'easing': 'linear'
        },
        paper_bgcolor='rgba(196, 196, 196, 0.8)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'showgrid': False},
        yaxis={'showgrid': False},
        title={
            'text': "Omrežnina",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font_family="Inter, sans-serif",
        font_size=15,
    )

    fig.update_yaxes(zerolinecolor='rgba(0,0,0,0)')

    # fig2.update_layout(bargap=0.3,
    #                    transition={
    #                        'duration': 300,
    #                        'easing': 'linear'
    #                    },
    #                    paper_bgcolor='rgba(196, 196, 196, 0.8)',
    #                    plot_bgcolor='rgba(0,0,0,0)',
    #                    xaxis={
    #                        'showgrid': False,
    #                        'tickmode': 'linear',
    #                        'tick0': 0,
    #                        'dtick': 1
    #                    },
    #                    yaxis={'showgrid': False})

    # fig2.update_yaxes(zerolinecolor='rgba(0,0,0,0)')
    return fig


def update_fig(fig, data):
    month_map = {
        1: "jan",
        2: "feb",
        3: "mar",
        4: "apr",
        5: "maj",
        6: "jun",
        7: "jul",
        8: "avg",
        9: "sep",
        10: "okt",
        11: "nov",
        12: "dec"
    }

    x = list(
        map(
            lambda x: x[0] + " " + x[1],
            list(
                zip(
                    list(
                        map(lambda x: month_map[x],
                            data["ts_results"]["month_num"])),
                    list(map(lambda x: str(x), data["ts_results"]["year"]))))))

    y = np.sum([
        data["ts_results"]["omr_p"], data["ts_results"]["omr_mt"],
        data["ts_results"]["pens"], data["ts_results"]["omr_vt"]
    ],
               axis=0)

    y1 = np.sum([
        data["ts_results"]["new_omr_p"], data["ts_results"]["new_omr_e"],
        data["ts_results"]["new_pens"]
    ],
                axis=0)

    fig = go.Figure(data=[
        go.Bar(x=x, y=y, name='Star sistem', marker={'color': '#C32025'})
    ])
    fig.add_trace(
        go.Bar(x=x,
               y=y1,
               name='Nov sistem',
               marker={'color': 'rgb(145, 145, 145)'}))

    fig.update_layout(
        bargap=0.3,
        transition={
            'duration': 300,
            'easing': 'linear'
        },
        paper_bgcolor='rgba(196, 196, 196, 0.8)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'showgrid': False},
        yaxis={'showgrid': False},
        title={
            'text':
            "Simulacija omrežnine za leto " +
            str(data["ts_results"]["year"][0]),
            'y':
            0.9,
            'x':
            0.5,
            'xanchor':
            'center',
            'yanchor':
            'top'
        },
        font_family="Inter, sans-serif",
        font_size=15,
    )

    fig.update_yaxes(title_text="Euro", zerolinecolor='rgba(0,0,0,0)')
    return fig


# Function to parse CSV content and return the children for displaying the filename
# and the session data for storing the DataFrame
def parse_contents(content, filename):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)

    try:
        print("Trying to read the file")
        if 'csv' in filename:
            # Assume that the user uploads a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploads an Excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return (html.Div(['Vnesi CSV or Excel datoteko.']), None)
        df.rename(columns={'Časovna značka': 'datetime'}, inplace=True)
        # df = df.fillna(0)
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Calculate net active and reactive power
        df['p'] = df['P+ Prejeta delovna moč'] - df['P- Oddana delovna moč']
        df['q'] = df['Q+ Prejeta jalova moč'] - df['Q- Oddana jalova moč']
        df['a'] = df['Energija A+'] - df['Energija A-']
        df['r'] = df['Energija R+'] - df['Energija R-']

        df = df[['datetime', 'p', 'q']]
        df = df.drop_duplicates(subset='datetime', keep='first')
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)
        df = df.resample('15min').mean()
        df.reset_index(inplace=True)
    except Exception as e:
        return (html.Div(['Napaka pri nalaganju.']), None)

    # If everything is fine, return the children for display and store the DataFrame in the session
    return (html.P(f"Dokument uspešno naložen."),
            df.to_dict('records'))