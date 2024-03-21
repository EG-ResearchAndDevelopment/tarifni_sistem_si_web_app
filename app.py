import numpy as np
from datetime import datetime
from collections import defaultdict 
import calendar
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash_extensions.enrich import Input, Output, DashProxy, MultiplexerTransform

from settlement import Settlement
from consmodel import PV, HP
from app_utils import *
from utils import handle_prikljucna_moc, find_min_obr_p

MONTHS = {
    'jan': True,
    'feb': False,
    'mar': False,
    'apr': False,
    'maj': False,
    'jun': False,
    'jul': False,
    'avg': False,
    'sep': False,
    'okt': False,
    'nov': False,
    'dec': False
}

settlement = Settlement()
timeseries_data = None
tech_data = None

mapping_prikljucna_moc = {  # priključna moč, obracunska moč, stevilo faz
    "4 kW (1x16 A)": [4, 3, 1],
    "5 kW (1x20 A)": [5, 3, 1],
    "6 kW (1x25 A)": [6, 6, 1],
    "7 kW (1x32 A)": [7, 7, 1],
    "8 kW (1x35 A)": [8, 7, 1],
    "11 kW (3x16 A)": [11, 7, 3],
    "14 kW (3x20 A)": [14, 7, 3],
    "17 kW (3x25 A)": [17, 10, 3],
    "22 kW (3x32 A)": [22, 22, 3],
    "24 kW (3x35 A)": [24, 24, 3],
    "28 kW (3x40 A)": [28, 28, 3],
    "35 kW (3x50 A)": [35, 35, 3],
    "43 kW (3x63 A)": [43, 43, 3],
    "55 kW (3x80 A)": [55, 55, 3],
    "69 kW (3x100 A)": [69, 69, 3],
    "86 kW (3x125 A)": [86, 86, 3],
    "110 kW (3x160 A)": [110, 110, 3],
    "138 kW (3x200 A)": [138, 138, 3],
    "drugo": [0, 0]
}

def def_value():
    return 0
mapping_prikljucna_obracunska_moc = defaultdict(def_value,{
    "4": 3,
    "5": 3,
    "6": 6,
    "7": 7,
    "8": 7,
    "11": 7,
    "14": 7,
    "17": 10,
    "22": 22,
    "24": 24,
    "28": 28,
    "35": 35,
    "43": 43,
    "55": 55,
    "69": 69,
    "86": 86,
    "110": 110,
    "138": 138,
})

mapping_tip_odjemalca = {
    "gospodinjski odjem": 1,
    "odjem na NN brez merjene moči": 2,
    "odjem na NN z merjeno močjo": 3,
    "Odjem na SN": 4,
    "Polnjenje EV": 6
}

omr5_res, omr2_res = "0€", "0€"


def create_empty_figure():
    global fig, fig2
    x = [
        'jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt',
        'nov', 'dec'
    ]
    x1 = np.arange(1, calendar.monthrange(2023, 1)[1] + 1, 1)
    y1 = np.random.randint(60, 100, calendar.monthrange(2023, 1)[1])
    y = np.zeros(12)

    fig = go.Figure(
        data=[go.Bar(x=x, y=y, name='2 tarifi', marker={'color': '#C32025'})])
    fig.add_trace(
        go.Bar(x=x,
               y=y,
               name='5 tarif',
               marker={'color': 'rgb(145, 145, 145)'}))

    fig2 = go.Figure(
        data=[go.Bar(x=x1, y=y1, name='2023', marker={'color': '#C32025'})])

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

    fig2.update_layout(bargap=0.3,
                       transition={
                           'duration': 300,
                           'easing': 'linear'
                       },
                       paper_bgcolor='rgba(196, 196, 196, 0.8)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       xaxis={
                           'showgrid': False,
                           'tickmode': 'linear',
                           'tick0': 0,
                           'dtick': 1
                       },
                       yaxis={'showgrid': False})

    fig2.update_yaxes(zerolinecolor='rgba(0,0,0,0)')


create_empty_figure()

error_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Error")),
        dbc.ModalBody("An error has occurred. Please try again."),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-error-modal", className="ml-auto")
        ),
    ],
    id="error-modal",
    is_open=False,  # The modal is closed by default
)

app = DashProxy(
    external_stylesheets=[dbc.themes.CYBORG, '/assets/mobile.css'],
    prevent_initial_callbacks=True,
    transforms=[MultiplexerTransform()],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.title = "Simulator tarifnega sistema"
server = app.server

app.layout = html.Div(children=[
    html.Div(
        children=[
            html.Div(
                id="mobile-header-div",
                className="mobile-header-div",
                children=[
                    html.Img(className="logo", src="./assets/images/logo-60.svg", style={'margin-bottom': '20px'}),
                ]),
            html.P('Simulator tarifnega sistema deluje le na računalniku. Glavni razlog, je uvažanje podatkov iz excel datoteke.')
        ],
        className="show-on-mobile",
    ),
    html.Div(children=[
        html.Div(
            id='header-div',
            className='header-div',
            children=[
                html.Img(className='logo', src="./assets/images/logo-60.svg"),
                html.Div(children=[
                    html.Div(
                        className='help-div',
                        children=[
                            dbc.Button(
                                "Pomoč",
                                id="open",
                                className="button-izracun",
                                n_clicks=0),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle(
                                        "Pomoč")),
                                    dbc.
                                    ModalBody(
                                        "Merilni podatki morajo biti v naslednji obliki:"
                                    ),
                                    html.Img(src="./assets/images/primer.jpg"),
                                    dbc.ModalBody(
                                        "V excel datoteki so lahko prisotni tudi drugi stolpci, je pa pomembno, da so prisotni vsaj ti stolpci, ki so prikazani na sliki. V primeru, da so prisotni tudi drugi stolpci, se bodo ti ignorirali."
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button("Close",
                                                id="close",
                                                className="button-izracun",
                                                n_clicks=0)),
                                ],
                                id="modal",
                                is_open=False,
                            ),
                        ]),
                    ],  
                    className="hide-on-mobile",
                ),
                html.P('EG-R&D'),
                html.
                A(target="_blank",
                href=
                "https://github.com/EG-ResearchAndDevelopment/tarifni_sistem_si_web_app",
                children=[
                    html.Img(className='git-logo',
                            src="./assets/images/github-logo1.svg"),
                ]),
            ]),
        ],
        className="hide-on-mobile",
    ),
    html.Div(
        children=[
            error_modal,
            html.Div(id='background-div',
                     className='background-div',
                     children=[
                         dcc.Graph(id='graph1',
                                   className='mesecni-graf',
                                   figure=fig,
                                   config={'displayModeBar': False}),
                     ]),
            html.Div(
                className='dialog-div',
                children=[
                    dcc.Input(
                        placeholder='Vstavi priključno moč...',
                        type="number",
                        value='',
                        className='prikljucna-moc-input',
                        id='prikljucna-moc',
                    ),
                    dcc.Dropdown(list(mapping_tip_odjemalca.keys()),
                                 value='Izberi tip odjemalca:',
                                 className='dropdown',
                                 id='tip-odjemalca'),
                    html.Div(children=[
                        dcc.Checklist(
                            [
                                ' Net metering - Samooskrba',
                                ' Meritve na zbiralkah'
                            ],
                            inline=True,
                            className='dropdown',
                            id='check-list',
                            style={
                                'margin-top': '10px',
                                'color': 'black'
                            },
                        ),
                    ]),
                    html.P('Določi predlagane obračunske moči:'),
                    html.Div(children=[
                        dcc.Input(id='predlagana-obracunska-moc-input1',
                                  className='merilno-mesto-input',
                                  placeholder='Blok 1',
                                  type="number"),
                        dcc.Input(id='predlagana-obracunska-moc-input2',
                                  className='merilno-mesto-input',
                                  placeholder='Blok 2',
                                  type="number"),
                        dcc.Input(id='predlagana-obracunska-moc-input3',
                                  className='merilno-mesto-input',
                                  placeholder='Blok 3',
                                  type="number"),
                        dcc.Input(id='predlagana-obracunska-moc-input4',
                                  className='merilno-mesto-input',
                                  placeholder='Blok 4',
                                  type="number"),
                        dcc.Input(id='predlagana-obracunska-moc-input5',
                                  className='merilno-mesto-input',
                                  placeholder='Blok 5',
                                  type="number"),
                    ]),
                    html.Div([
                        html.P("Naloži podatke o porabi v formatu MojElektro:",
                               ),
                        dcc.Upload(
                            id='upload-data',
                            className='upload-data',
                            children=html.Div(
                                [html.P('Izberi datoteko: 15 min podatki')]),
                            multiple=True),
                        html.Div(id='output-data-upload'),
                    ],
                             style={
                                 'margin-top': '20px',
                                 'margin-bottom': '30px',
                             }),
                    html.Div(children=[
                        dcc.Input(id='pv-size',
                                  className='merilno-mesto-input',
                                  placeholder='Velikost simulirane SE',
                                  type="number"),
                        dcc.Checklist(
                            [
                                ' Simuliraj sončno elektrarno',
                                ' Simuliraj toplotno črpalko'
                            ],
                            inline=True,
                            className='dropdown',
                            id='simulate',
                            style={
                                'margin-top': '10px',
                                'color': 'black'
                            },
                        ),
                    ]),
                    dcc.Loading(id="ls-loading-1",
                                className='loading',
                                color='#C32025',
                                children=[
                                    html.Button(id='button-izracun',
                                                className='button-izracun',
                                                children='Izračun')
                                ],
                                type="circle"),
                ]),
            html.Div(id='omreznina1-top-div',
                     className='omreznina1-top-div',
                     children=[
                         html.Div(className='main',
                                  children=[
                                      html.Div(children=[
                                          html.H5('OMREŽNINA 5T'),
                                          html.H4(id='cena-5t',
                                                  children=['0€'])
                                      ])
                                  ]),
                         html.Div(className='bubble',
                                  children=[
                                      html.Img(
                                          src='./assets/images/icon_share.svg')
                                  ]),
                         html.Div(className='bubble2'),
                     ]),
            html.Div(id='omreznina-top-div',
                     className='omreznina-top-div',
                     children=[
                         html.Div(className='main',
                                  children=[
                                      html.Div(children=[
                                          html.H5('OMREŽNINA 2T'),
                                          html.H4(id='cena-2t',
                                                  children=['0€'])
                                      ])
                                  ]),
                         html.Div(className='bubble',
                                  children=[
                                      html.Img(
                                          src='./assets/images/icon_share.svg')
                                  ]),
                         html.Div(className='bubble2'),
                     ]),
            html.Div(id='energija-top-div',
                     className='energija-top-div',
                     children=[
                         html.Div(className='main',
                                  children=[
                                      html.Div(children=[
                                          html.H5('ENERGIJA'),
                                          html.H4('KMALU')
                                      ])
                                  ]),
                         html.Div(
                             className='bubble',
                             children=[
                                 html.Img(
                                     src='./assets/images/icon_energija.svg')
                             ]),
                         html.Div(className='bubble2'),
                     ]),
            html.Div(id='prispevki-top-div',
                     className='prispevki-top-div',
                     children=[
                         html.Div(className='main',
                                  children=[
                                      html.Div(children=[
                                          html.H5('PRISPEVKI'),
                                          html.H4('KMALU')
                                      ])
                                  ]),
                         html.Div(
                             className='bubble',
                             children=[
                                 html.Img(
                                     src='./assets/images/icon_prispevki.svg')
                             ]),
                         html.Div(className='bubble2'),
                     ]),
        ],
        className="hide-on-mobile",
    ),
    dcc.Store(id="store", data=MONTHS),
])

PRIKLJUCNA_MOC = 0
MIN_OBR_P = 0



@app.callback(
    [
        Output('graph1', 'figure'),
        Output('button-izracun', 'n_clicks'),
        Output('cena-2t', 'children'),
        Output('cena-5t', 'children'),
        Output('predlagana-obracunska-moc-input1', 'value'),
        Output('predlagana-obracunska-moc-input2', 'value'),
        Output('predlagana-obracunska-moc-input3', 'value'),
        Output('predlagana-obracunska-moc-input4', 'value'),
        Output('predlagana-obracunska-moc-input5', 'value'),
        Output('pv-size', 'value'),
    ],
    [
        Input('button-izracun', 'n_clicks'),
        Input('prikljucna-moc', 'value'),
        Input('tip-odjemalca', 'value'),
        Input('check-list', 'value'),
        Input('predlagana-obracunska-moc-input1', 'value'),
        Input('predlagana-obracunska-moc-input2', 'value'),
        Input('predlagana-obracunska-moc-input3', 'value'),
        Input('predlagana-obracunska-moc-input4', 'value'),
        Input('predlagana-obracunska-moc-input5', 'value'),
        Input('simulate', 'value'),
        Input('pv-size', 'value'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
    ],
)
def update_graph(clicks, prikljucna_moc, tip_odjemalca, check_list,
                 predlagana_obracunska_moc1, predlagana_obracunska_moc2,
                 predlagana_obracunska_moc3, predlagana_obracunska_moc4,
                 predlagana_obracunska_moc5, simulate, pv_size,
                 list_of_contents, list_of_names):
    global fig
    global timeseries_data
    global omr5_res, omr2_res
    global PRIKLJUCNA_MOC, MIN_OBR_P

    # check if prikljucna_moc has changed
    try:
        if prikljucna_moc != PRIKLJUCNA_MOC:
            PRIKLJUCNA_MOC = prikljucna_moc
            MIN_OBR_P = round(
                find_min_obr_p(1 if int(prikljucna_moc) <= 8 else 3,
                            prikljucna_moc), 1)
            predlagana_obracunska_moc1 = MIN_OBR_P
            predlagana_obracunska_moc2 = MIN_OBR_P
            predlagana_obracunska_moc3 = MIN_OBR_P
            predlagana_obracunska_moc4 = MIN_OBR_P
            predlagana_obracunska_moc5 = MIN_OBR_P

        if any(x < MIN_OBR_P for x in [
            predlagana_obracunska_moc1, predlagana_obracunska_moc2,
            predlagana_obracunska_moc3, predlagana_obracunska_moc4,
            predlagana_obracunska_moc5]):
            return fig, 0, omr2_res, omr5_res, predlagana_obracunska_moc1, predlagana_obracunska_moc2, predlagana_obracunska_moc3, predlagana_obracunska_moc4, predlagana_obracunska_moc5, pv_size
    except:
        error = f"Predlagane obračunske moči morajo biti večje ali enake minimalni obračunski moči: {MIN_OBR_P}"
        return fig, 0, omr2_res, omr5_res, predlagana_obracunska_moc1, predlagana_obracunska_moc2, predlagana_obracunska_moc3, predlagana_obracunska_moc4, predlagana_obracunska_moc5, pv_size
        pass

    net_metering = 0
    zbiralke = 0
    if check_list is not None:
        if " Net metering - Samooskrba" in check_list:
            net_metering = 1
        if " Meritve na zbiralkah" in check_list:
            zbiralke = 1

    if prikljucna_moc == None:
        prikljucna_moc = "drugo"
    if tip_odjemalca == None:
        tip_odjemalca = "gospodinjski odjem"

    if clicks is not None:
        if clicks == 1:
            # correct predlagane obracunske moci
            obr_p_correct = handle_prikljucna_moc([
                predlagana_obracunska_moc1, predlagana_obracunska_moc2,
                predlagana_obracunska_moc3, predlagana_obracunska_moc4,
                predlagana_obracunska_moc5
            ], MIN_OBR_P)
            predlagana_obracunska_moc1 = obr_p_correct[0]
            predlagana_obracunska_moc2 = obr_p_correct[1]
            predlagana_obracunska_moc3 = obr_p_correct[2]
            predlagana_obracunska_moc4 = obr_p_correct[3]
            predlagana_obracunska_moc5 = obr_p_correct[4]

            if list_of_contents is not None:
                children = [
                    parse_contents(c, n)
                    for c, n in zip(list_of_contents, list_of_names)
                ]
            else:
                children = None

            if children is not None:
                for child in children:
                    if child is not None:
                        timeseries_data = child[1]
                        break

            # check if the data is loaded
            if timeseries_data is not None:
                data = timeseries_data
                # extract start and end date and convert it to datetime.datetime object
                start = pd.to_datetime(
                    datetime.datetime.strptime(str(data.datetime.iloc[0]),
                                               "%Y-%m-%d %H:%M:%S"))
                end = pd.to_datetime(
                    datetime.datetime.strptime(str(data.datetime.iloc[-1]),
                                               "%Y-%m-%d %H:%M:%S"))
                # convert to datetime object

                lat = 46.155768
                lon = 14.304951
                alt = 400
                if simulate is not None:
                    if " Simuliraj sončno elektrarno" in simulate:
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
                        timeseries_data[
                            "p"] = timeseries_data["p"] - pv_timeseries.values
                    if " Simuliraj toplotno črpalko" in simulate:
                        hp = HP(lat, lon, alt)
                        hp_timeseries = hp.simulate(22.0,
                                                    start=start,
                                                    end=end,
                                                    freq='15min')
                        # difference between the two timeseries
                        timeseries_data[
                            "p"] = timeseries_data["p"] + hp_timeseries.values
            else:
                return fig, 0, omr2_res, omr5_res, predlagana_obracunska_moc1, predlagana_obracunska_moc2, predlagana_obracunska_moc3, predlagana_obracunska_moc4, predlagana_obracunska_moc5, pv_size
            tech_data = {
                "blocks": [
                    predlagana_obracunska_moc1, predlagana_obracunska_moc2,
                    predlagana_obracunska_moc3, predlagana_obracunska_moc4,
                    predlagana_obracunska_moc5
                ],
                "prikljucna_moc":
                prikljucna_moc,
                "obracunska_moc":
                mapping_prikljucna_obracunska_moc[prikljucna_moc],
                "consumer_type_id":
                mapping_tip_odjemalca[tip_odjemalca],
                "samooskrba":
                net_metering,
                "zbiralke":
                zbiralke,
                "trenutno_stevilo_tarif":
                2,
                "stevilo_faz":
                1 if int(prikljucna_moc) <=8 else 3,
            }
            print(tech_data)
            settlement.calculate_settlement(0,
                                            timeseries_data,
                                            tech_data,
                                            calculate_blocks=False,
                                            override_year=False)

            data = settlement.output
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
                            list(
                                map(lambda x: str(x),
                                    data["ts_results"]["year"]))))))

            y = np.sum([
                data["ts_results"]["omr_p"], data["ts_results"]["omr_mt"],
                data["ts_results"]["pens"], data["ts_results"]["omr_vt"]
            ],
                       axis=0)

            y1 = np.sum([
                data["ts_results"]["new_omr_p"],
                data["ts_results"]["new_omr_e"], data["ts_results"]["new_pens"]
            ],
                        axis=0)

            fig = go.Figure(data=[
                go.Bar(x=x, y=y, name='2 tarifi', marker={'color': '#C32025'})
            ])
            fig.add_trace(
                go.Bar(x=x,
                       y=y1,
                       name='5 tarif',
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
                    'text': str(data["ts_results"]["year"][0]),
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                font_family="Inter, sans-serif",
                font_size=15,
            )

            fig.update_yaxes(title_text="Euro", zerolinecolor='rgba(0,0,0,0)')

            omr2_res = '%.2f€' % np.sum(y)
            omr5_res = '%.2f€' % np.sum(y1)
            return fig, 0, omr2_res, omr5_res, predlagana_obracunska_moc1, predlagana_obracunska_moc2, predlagana_obracunska_moc3, predlagana_obracunska_moc4, predlagana_obracunska_moc5, pv_size
        # else:
        #     create_empty_figure()
    return fig, 0, omr2_res, omr5_res, predlagana_obracunska_moc1, predlagana_obracunska_moc2, predlagana_obracunska_moc3, predlagana_obracunska_moc4, predlagana_obracunska_moc5, pv_size


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"),
     Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("error-modal", "is_open"),
    [Input("close-error-modal", "n_clicks")],
    [State("error-modal", "is_open")],
)
def toggle_error_modal(close_error_clicks, is_open):
    if close_error_clicks:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
