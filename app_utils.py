import base64
import calendar
import datetime
import io

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from consmodel import HP, PV
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

    # Data for new system segmented into three parts for stacking
    new_omr_p = data["ts_results"]["new_omr_p"]
    new_omr_e = data["ts_results"]["new_omr_e"]
    new_pens = data["ts_results"]["new_pens"]
    # Data for old and new systems
    y_old = np.sum([
        data["ts_results"]["omr_p"], data["ts_results"]["omr_mt"],
        data["ts_results"]["pens"], data["ts_results"]["omr_vt"]
    ],
               axis=0)
    new_omr_p = data["ts_results"]["new_omr_p"]
    new_omr_e = data["ts_results"]["new_omr_e"]
    new_pens = data["ts_results"]["new_pens"]

    # Create a figure with grouped bars for the old system
    fig = go.Figure(
        data=[
            go.Bar(
                name='Star sistem',
                x=x,
                y=y_old,
                marker={'color': '#C32025'},
                offsetgroup=0,
                width=0.4,
                offset=0.23,
            ),
            go.Bar(
                name='Nov - omrežnina na energijo',
                x=x,
                y=new_omr_e,
                marker={'color': '#D3D3D3'},  # LightGrey
                offsetgroup=1,
                width=0.4,
                base=np.add(new_omr_p, new_pens),  # Start stacking from top of new_omr_e
            ),
            go.Bar(
                name='Nov - penali',
                x=x,
                y=new_pens,
                marker={'color': '#808080'},  # Grey
                offsetgroup=1,
                width=0.4,
                base=new_omr_p,  # Start stacking from top of new_omr_p
            ),
            # The new system's bars are split into 3 parts for the stacked effect
            go.Bar(
                name='Nov - omrežnina na moč',
                x=x,
                y=new_omr_p,
                marker={'color': '#A9A9A9'},  # DarkGrey
                offsetgroup=1,
                width=0.4,
                base=0,  # Start stacking from 0
            ),
        ]
    )
    fig.update_layout(
        barmode='stack',
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
    fig.update_traces(marker_line_width=1, marker_line_color='rgba(0,0,0,0)')
    fig.update_yaxes(title_text="Euro", zerolinecolor='rgba(0,0,0,0)')
    return fig


def parse_contents(content, filename):
    _, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    try:
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
        # df['a'] = df['Energija A+'] - df['Energija A-']
        # if q is nan, set it to 0
        if "q" in df.columns:
            df.loc[df['q'].isnull(), 'q'] = 0
        if "Blok" in df.columns:
            # rename blok to block
            df.rename(columns={'Blok': 'block'}, inplace=True)
            df = df[['datetime', 'p', 'q', 'block']]
        else:
            df = df[['datetime', 'p', 'q']]
        df = df.drop_duplicates(subset='datetime', keep='first')
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)
        df = df.resample('15min').interpolate()
        df.reset_index(inplace=True)
    except Exception as e:
        print(e)
        return (html.Div(['Napaka pri nalaganju.']), None)

    # If everything is fine, return the children for display and store the DataFrame in the session
    return (html.Div(f"Dokument uspešno naložen."), df.to_dict('records'))


####################################################################################################
#
# Helper functions for the SIMULATION
#
####################################################################################################
def simulate_additional_elements(timeseries_data, simulate_params, pv_size):
    if simulate_params is not None:
        # extract start and end date and convert it to datetime.datetime object
        start = pd.to_datetime(
            datetime.datetime.strptime(str(timeseries_data.datetime.iloc[0]),
                                       "%Y-%m-%dT%H:%M:%S"))
        end = pd.to_datetime(
            datetime.datetime.strptime(str(timeseries_data.datetime.iloc[-1]),
                                       "%Y-%m-%dT%H:%M:%S"))
        lat = 46.155768
        lon = 14.304951
        alt = 400
        if " Simuliraj novo sončno elektrarno" in simulate_params:
            pv = PV(lat=lat,
                    lon=lon,
                    alt=alt,
                    index=1,
                    name="test",
                    tz="Europe/Vienna")
            if pv_size is None:
                pv_size = 10
            pv_timeseries = pv.simulate(
                pv_size=pv_size,
                start=start,
                end=end,
                freq="15min",
                model="ineichen",
                consider_cloud_cover=True,
            )
            # difference between the two timeseries
            timeseries_data["p"] = timeseries_data["p"] - pv_timeseries.values
        if " Simuliraj novo toplotno črpalko" in simulate_params:
            hp = HP(lat, lon, alt)
            hp_timeseries = hp.simulate(22.0,
                                        start=start,
                                        end=end,
                                        freq='15min')
            # difference between the two timeseries
            timeseries_data["p"] = timeseries_data["p"] + hp_timeseries.values
    return timeseries_data, pv_size


def generate_results(results, session_results):
    omr_old = np.sum([
        results["ts_results"]["omr_p"], results["ts_results"]["omr_mt"],
        results["ts_results"]["pens"], results["ts_results"]["omr_vt"]
    ],
                     axis=0)

    omr_new = np.sum([
        results["ts_results"]["new_omr_p"], results["ts_results"]["new_omr_e"],
        results["ts_results"]["new_pens"]
    ],
                     axis=0)
    omr2_res = '%.2f€' % np.sum(omr_old)
    omr5_res = '%.2f€' % np.sum(omr_new)
    energy_res = '%.2f€' % np.sum(results["ts_results"]["e_mt"] +
                                  results["ts_results"]["e_vt"])
    prispevki_res = '%.2f€' % np.sum(results["ts_results"]["ove_spte_p"] +
                                     results["ts_results"]["ove_spte_e"])
    session_results.update({
        "omr2": omr2_res,
        "omr5": omr5_res,
        "energija-res": energy_res,
        "prispevki-res": prispevki_res
    })
    return session_results