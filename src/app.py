import numpy as np
import pandas as pd
import calendar
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash_extensions.enrich import Input, Output, DashProxy, MultiplexerTransform

from settlement import Settlement
from read_elektro_csv import read_moj_elektro_csv

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


def get_data(mm):
    obracunska_moc_mapping = {
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "11": 11,
        "14": 14,
        "17": 17,
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
        "drugo": 0
    }

    # read data
    # KRIŽNAR
    path = r"data/6-123604-15minMeritve2023-01-01-2023-12-31.xlsx"
    data = read_moj_elektro_csv(path)
    tech_data = {
        "blocks": [0, 0, 0, 0, 0],
        "prikljucna_moc": "17 kW (3x25 A)",
        "consumer_type_id": 1,
        "samooskrba": 0,
        "zbiralke": 0,
        "trenutno_stevilo_tarif": 2,
        "stevilo_faz": None
    }
    # PETROVIC

    # 1 - gospodinjski odjem (us0)
    # 2 - odjem na nn brez merjene moči (us0, us1)
    # 3 - odjem na nn z merjeno močjo (us0, us1)
    # 4 - Odjem na SN (us2, us3)
    # 6 - Polnjenje EV

    mapping = {  # priključna moč, obracunska moč, stevilo faz, consumer_type_id
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
    tech_data["stevilo_faz"] = mapping[tech_data["prikljucna_moc"]][2]
    tech_data["obracunska_moc"] = mapping[tech_data["prikljucna_moc"]][1]
    tech_data["prikljucna_moc"] = mapping[tech_data["prikljucna_moc"]][0]
    settlement = Settlement()

    settlement.calculate_settlement(0, data, tech_data)
    print(settlement.output)

    nova_omreznina = settlement.output["ts_results"]["new_omr_p"] + settlement.output["ts_results"][
        "new_omr_e"] + settlement.output["ts_results"]["new_pens"]
    trenutna_omreznina = settlement.output["ts_results"]["omr_p"] + settlement.output["ts_results"][
        "omr_vt"] + settlement.output["ts_results"]["omr_mt"]
    print("nova omreznina: ", np.sum(nova_omreznina))
    print("trenutna omreznina: ", np.sum(trenutna_omreznina))
    data = settlement.output

    return data


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
    go.Bar(x=x, y=y, name='5 tarif', marker={'color': 'rgb(145, 145, 145)'}))
# fig.add_trace(go.Bar(x=x, y=y1, name='5 tarif', marker={'color': 'rgb(145, 145, 145)'}))
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

app = DashProxy(external_stylesheets=[dbc.themes.CYBORG],
                prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()])
server = app.server

app.layout = html.Div(children=[
    html.Div(id='header-div',
             className='header-div',
             children=[
                 html.Img(className='logo', src="./assets/images/logo-60.svg")
             ]),
    html.Div(id='background-div',
             className='background-div',
             children=[
                 dcc.Graph(id='graph1',
                           className='mesecni-graf',
                           figure=fig,
                           config={'displayModeBar': False}),
             ]),
    html.Div(className='dialog-div',
             children=[
                 dcc.Input(id='merilno-mesto-input',
                           className='merilno-mesto-input',
                           placeholder='Merilno mesto',
                           type="number"),
                 dcc.Loading(id="ls-loading-1",
                             className='loading',
                             color='#C32025',
                             children=[
                                 html.Button(id='button-izracun',
                                             className='button-izracun',
                                             children='Izračun'),
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
                                  html.H4(id='cena-5t', children=['0€'])
                              ])
                          ]),
                 html.Div(
                     className='bubble',
                     children=[html.Img(
                         src='./assets/images/icon_share.svg')]),
                 html.Div(className='bubble2'),
             ]),
    html.Div(id='omreznina-top-div',
             className='omreznina-top-div',
             children=[
                 html.Div(className='main',
                          children=[
                              html.Div(children=[
                                  html.H5('OMREŽNINA 2T'),
                                  html.H4(id='cena-2t', children=['0€'])
                              ])
                          ]),
                 html.Div(
                     className='bubble',
                     children=[html.Img(
                         src='./assets/images/icon_share.svg')]),
                 html.Div(className='bubble2'),
             ]),
    html.Div(
        id='energija-top-div',
        className='energija-top-div',
        children=[
            html.Div(
                className='main',
                children=[
                    html.Div(children=[html.H5(
                        'ENERGIJA'), html.H4('SOON')])
                ]),
            html.Div(
                className='bubble',
                children=[html.Img(src='./assets/images/icon_energija.svg')]),
            html.Div(className='bubble2'),
        ]),
    html.Div(id='prispevki-top-div',
             className='prispevki-top-div',
             children=[
                 html.Div(
                     className='main',
                     children=[
                         html.Div(
                             children=[html.H5('PRISPEVKI'),
                                       html.H4('SOON')])
                     ]),
                 html.Div(className='bubble',
                          children=[
                              html.Img(
                                  src='./assets/images/icon_prispevki.svg')
                          ]),
                 html.Div(className='bubble2'),
             ]),

    # html.Div(
    #     className='letni-graf-div',
    #     children=[
    #         dcc.Graph(
    #             className='letni-graf',
    #             figure=fig2,
    #             config={
    #                 'displayModeBar': False
    #             }
    #         )
    #     ]
    # ),
    html.Div(className='predstavitev-sistema-div',
             children=[
                 html.Div(className='mesec-div',
                          children=[
                              html.Div(className='naslov',
                                       children=[html.H4('Izberite mesec')]),
                              html.Div(className='meseci',
                                       children=[
                                           html.Div(id='jan',
                                                    className='jan',
                                                    children=[
                                                        html.H5(
                                                            id='jan-h5',
                                                            className='jan-h5',
                                                            children=['JAN']),
                                                    ]),
                                           html.Div(id='feb',
                                                    className='feb',
                                                    children=[
                                                        html.H5(
                                                            id='feb-h5',
                                                            className='feb-h5',
                                                            children=['FEB']),
                                                    ]),
                                           html.Div(id='mar',
                                                    className='mar',
                                                    children=[
                                                        html.H5(
                                                            id='mar-h5',
                                                            className='mar-h5',
                                                            children=['MAR']),
                                                    ]),
                                           html.Div(id='apr',
                                                    className='apr',
                                                    children=[
                                                        html.H5(
                                                            id='apr-h5',
                                                            className='apr-h5',
                                                            children=['APR']),
                                                    ]),
                                           html.Div(id='maj',
                                                    className='maj',
                                                    children=[
                                                        html.H5(
                                                            id='maj-h5',
                                                            className='maj-h5',
                                                            children=['MAJ']),
                                                    ]),
                                           html.Div(id='jun',
                                                    className='jun',
                                                    children=[
                                                        html.H5(
                                                            id='jun-h5',
                                                            className='jun-h5',
                                                            children=['JUN']),
                                                    ]),
                                           html.Div(id='jul',
                                                    className='jul',
                                                    children=[
                                                        html.H5(
                                                            id='jul-h5',
                                                            className='jul-h5',
                                                            children=['JUL']),
                                                    ]),
                                           html.Div(id='avg',
                                                    className='avg',
                                                    children=[
                                                        html.H5(
                                                            id='avg-h5',
                                                            className='avg-h5',
                                                            children=['AVG']),
                                                    ]),
                                           html.Div(id='sep',
                                                    className='sep',
                                                    children=[
                                                        html.H5(
                                                            id='sep-h5',
                                                            className='sep-h5',
                                                            children=['SEP']),
                                                    ]),
                                           html.Div(id='okt',
                                                    className='okt',
                                                    children=[
                                                        html.H5(
                                                            id='okt-h5',
                                                            className='okt-h5',
                                                            children=['OKT']),
                                                    ]),
                                           html.Div(id='nov',
                                                    className='nov',
                                                    children=[
                                                        html.H5(
                                                            id='nov-h5',
                                                            className='nov-h5',
                                                            children=['NOV']),
                                                    ]),
                                           html.Div(id='dec',
                                                    className='dec',
                                                    children=[
                                                        html.H5(
                                                            id='dec-h5',
                                                            className='dec-h5',
                                                            children=['DEC']),
                                                    ]),
                                       ]),
                              html.Div(className='podnapisi',
                                       children=[
                                           html.Div(className='podnapis1',
                                                    children=[
                                                        html.H5(
                                                            'višja sezona'),
                                                    ]),
                                           html.Div(className='podnapis2',
                                                    children=[
                                                        html.H5(
                                                            'nižja sezona'),
                                                    ]),
                                           html.Div(className='podnapis3',
                                                    children=[
                                                        html.H5(
                                                            'višja sezona'),
                                                    ]),
                                       ]),
                              html.Div(
                                  className='question',
                                  children=[
                                      html.Img(
                                          src=
                                          './assets/images/icon_question.svg')
                                  ]),
                          ]),
                 html.Div(className='dan-div',
                          children=[
                              html.Div(className='naslov',
                                       children=[html.H4('Izberite dan')]),
                              html.Div(className='dnevi',
                                       children=[
                                           html.Div(id='pon',
                                                    className='pon',
                                                    children=[
                                                        html.H5(
                                                            id='pon-h5',
                                                            className='pon-h5',
                                                            children=['PON']),
                                                    ]),
                                           html.Div(id='tor',
                                                    className='tor',
                                                    children=[
                                                        html.H5(
                                                            id='tor-h5',
                                                            className='tor-h5',
                                                            children=['TOR']),
                                                    ]),
                                           html.Div(id='sre',
                                                    className='sre',
                                                    children=[
                                                        html.H5(
                                                            id='sre-h5',
                                                            className='sre-h5',
                                                            children=['SRE']),
                                                    ]),
                                           html.Div(id='cet',
                                                    className='cet',
                                                    children=[
                                                        html.H5(
                                                            id='cet-h5',
                                                            className='cet-h5',
                                                            children=['ČET']),
                                                    ]),
                                           html.Div(id='pet',
                                                    className='pet',
                                                    children=[
                                                        html.H5(
                                                            id='pet-h5',
                                                            className='pet-h5',
                                                            children=['PET']),
                                                    ]),
                                           html.Div(id='sob',
                                                    className='sob',
                                                    children=[
                                                        html.H5(
                                                            id='sob-h5',
                                                            className='sob-h5',
                                                            children=['SOB']),
                                                    ]),
                                           html.Div(id='ned',
                                                    className='ned',
                                                    children=[
                                                        html.H5(
                                                            id='ned-h5',
                                                            className='ned-h5',
                                                            children=['NED']),
                                                    ]),
                                       ]),
                              html.Div(className='podnapisi',
                                       children=[
                                           html.Div(className='podnapis1',
                                                    children=[
                                                        html.H5('delovni dan'),
                                                    ]),
                                           html.Div(className='podnapis2',
                                                    children=[
                                                        html.H5(
                                                            'dela prost dan'),
                                                    ]),
                                       ]),
                              html.Div(
                                  className='question',
                                  children=[
                                      html.Img(
                                          src=
                                          './assets/images/icon_question.svg')
                                  ]),
                          ]),
                 html.Div(className='blok-div',
                          children=[
                              html.Div(className='naslov',
                                       children=[html.H4('Izberite blok')]),
                              html.Div(
                                  className='bloki',
                                  children=[
                                      html.Div(
                                          id='blok1',
                                          className='blok1',
                                          children=[
                                              html.P(id='blok1-h5',
                                                     className='blok1-h5',
                                                     children=['00:00-06:00']),
                                          ]),
                                      html.Div(
                                          id='blok2',
                                          className='blok2',
                                          children=[
                                              html.P(id='blok2-h5',
                                                     className='blok2-h5',
                                                     children=['06:00-07:00']),
                                          ]),
                                      html.Div(
                                          id='blok3',
                                          className='blok3',
                                          children=[
                                              html.P(id='blok3-h5',
                                                     className='blok3-h5',
                                                     children=['07:00-14:00']),
                                          ]),
                                      html.Div(
                                          id='blok4',
                                          className='blok4',
                                          children=[
                                              html.P(id='blok4-h5',
                                                     className='blok4-h5',
                                                     children=['14:00-16:00']),
                                          ]),
                                      html.Div(
                                          id='blok5',
                                          className='blok5',
                                          children=[
                                              html.P(id='blok5-h5',
                                                     className='blok5-h5',
                                                     children=['16:00-20:00']),
                                          ]),
                                      html.Div(
                                          id='blok6',
                                          className='blok6',
                                          children=[
                                              html.P(id='blok6-h5',
                                                     className='blok6-h5',
                                                     children=['20:00-22:00']),
                                          ]),
                                      html.Div(
                                          id='blok7',
                                          className='blok7',
                                          children=[
                                              html.P(id='blok7-h5',
                                                     className='blok7-h5',
                                                     children=['22:00-24:00']),
                                          ]),
                                  ]),
                              html.Div(
                                  className='podnapisi',
                                  children=[
                                      html.Img(
                                          id='blok1-slika',
                                          src='./assets/images/evri3.svg'),
                                      html.Img(
                                          id='blok2-slika',
                                          src='./assets/images/evri2.svg'),
                                      html.Img(
                                          id='blok3-slika',
                                          src='./assets/images/evri1.svg'),
                                      html.Img(
                                          id='blok4-slika',
                                          src='./assets/images/evri2.svg'),
                                      html.Img(
                                          id='blok5-slika',
                                          src='./assets/images/evri1.svg'),
                                      html.Img(
                                          id='blok6-slika',
                                          src='./assets/images/evri2.svg'),
                                      html.Img(
                                          id='blok7-slika',
                                          src='./assets/images/evri3.svg'),
                                  ]),
                              html.Div(
                                  className='postavka',
                                  children=[
                                      html.Img(
                                          src='./assets/images/line.svg'),
                                      html.H3(id='cena',
                                              className='cena-energije',
                                              children=['0 €/kwh']),
                                      html.P(className='tarifa-energije',
                                             children=['Tarifa energije']),
                                      html.H3(id='cena-moc',
                                              className='cena-moci',
                                              children=['0 €/kw']),
                                      html.P(className='tarifa-moci',
                                             children=['Tarifa moči']),
                                      html.H3(id='blok-ura',
                                              className='blok-ura',
                                              children=['00:00 - 06:00']),
                                      html.P(className='casovni-blok',
                                             children=['Časovni blok']),
                                      html.H3(id='predlagana-obr-moc',
                                              className='predlagana-obr-moc',
                                              children=['0 kw']),
                                      html.P(className='obr-moc-subtitle',
                                             children=[
                                                 'Predlagana obračunska moč'
                                             ]),
                                  ]),
                          ]),
             ]),
    dcc.Store(id="store", data=MONTHS),
])

SEZONA = 'zima'
DAN = 'delavnik'
BLOK = 'blok1'

CENA1, CENA2, CENA3, CENA4, CENA5 = 0, 0, 0, 0, 0
CENA6, CENA7, CENA8, CENA9, CENA10 = 0, 0, 0, 0, 0
OBR_MOC1, OBR_MOC2, OBR_MOC3, OBR_MOC4, OBR_MOC5 = 0, 0, 0, 0, 0


@app.callback(
    [
        Output('cena', 'children'),
        Output('cena-moc', 'children'),
        Output('predlagana-obr-moc', 'children'),
        Output('jan', 'n_clicks'),
        Output('feb', 'n_clicks'),
        Output('mar', 'n_clicks'),
        Output('apr', 'n_clicks'),
        Output('maj', 'n_clicks'),
        Output('jun', 'n_clicks'),
        Output('jul', 'n_clicks'),
        Output('avg', 'n_clicks'),
        Output('sep', 'n_clicks'),
        Output('okt', 'n_clicks'),
        Output('nov', 'n_clicks'),
        Output('dec', 'n_clicks'),
        Output('pon', 'n_clicks'),
        Output('tor', 'n_clicks'),
        Output('sre', 'n_clicks'),
        Output('cet', 'n_clicks'),
        Output('pet', 'n_clicks'),
        Output('sob', 'n_clicks'),
        Output('ned', 'n_clicks'),
        Output('blok1', 'n_clicks'),
        Output('blok2', 'n_clicks'),
        Output('blok3', 'n_clicks'),
        Output('blok4', 'n_clicks'),
        Output('blok5', 'n_clicks'),
        Output('blok6', 'n_clicks'),
        Output('blok7', 'n_clicks'),
    ],
    [
        Input('jan', 'n_clicks'),
        Input('feb', 'n_clicks'),
        Input('mar', 'n_clicks'),
        Input('apr', 'n_clicks'),
        Input('maj', 'n_clicks'),
        Input('jun', 'n_clicks'),
        Input('jul', 'n_clicks'),
        Input('avg', 'n_clicks'),
        Input('sep', 'n_clicks'),
        Input('okt', 'n_clicks'),
        Input('nov', 'n_clicks'),
        Input('dec', 'n_clicks'),
        Input('pon', 'n_clicks'),
        Input('tor', 'n_clicks'),
        Input('sre', 'n_clicks'),
        Input('cet', 'n_clicks'),
        Input('pet', 'n_clicks'),
        Input('sob', 'n_clicks'),
        Input('ned', 'n_clicks'),
        Input('blok1', 'n_clicks'),
        Input('blok2', 'n_clicks'),
        Input('blok3', 'n_clicks'),
        Input('blok4', 'n_clicks'),
        Input('blok5', 'n_clicks'),
        Input('blok6', 'n_clicks'),
        Input('blok7', 'n_clicks'),
    ],
)
def change_cena(jan, feb, mar, apr, maj, jun, jul, avg, sep, okt, nov, dec,
                pon, tor, sre, cet, pet, sob, ned, blok1, blok2, blok3, blok4,
                blok5, blok6, blok7):
    global SEZONA, DAN, BLOK, CENA1, CENA2, CENA3, CENA4, CENA5, CENA6, CENA7, CENA8, CENA9, CENA10
    global OBR_MOC1, OBR_MOC2, OBR_MOC3, OBR_MOC4, OBR_MOC5

    if jan is not None:
        if jan == 1:
            SEZONA = 'zima'
    if feb is not None:
        if feb == 1:
            SEZONA = 'zima'
    if mar is not None:
        if mar == 1:
            SEZONA = 'vmes'
    if apr is not None:
        if apr == 1:
            SEZONA = 'vmes'
    if maj is not None:
        if maj == 1:
            SEZONA = 'vmes'
    if jun is not None:
        if jun == 1:
            SEZONA = 'vmes'
    if jul is not None:
        if jul == 1:
            SEZONA = 'vmes'
    if avg is not None:
        if avg == 1:
            SEZONA = 'vmes'
    if sep is not None:
        if sep == 1:
            SEZONA = 'vmes'
    if okt is not None:
        if okt == 1:
            SEZONA = 'vmes'
    if nov is not None:
        if nov == 1:
            SEZONA = 'zima'
    if dec is not None:
        if dec == 1:
            SEZONA = 'zima'
    if pon is not None:
        if pon == 1:
            DAN = 'delavnik'
    if tor is not None:
        if tor == 1:
            DAN = 'delavnik'
    if sre is not None:
        if sre == 1:
            DAN = 'delavnik'
    if cet is not None:
        if cet == 1:
            DAN = 'delavnik'
    if pet is not None:
        if pet == 1:
            DAN = 'delavnik'
    if sob is not None:
        if sob == 1:
            DAN = 'vikend'
    if ned is not None:
        if ned == 1:
            DAN = 'vikend'
    if blok1 is not None:
        if blok1 == 1:
            BLOK = 'blok1'
    if blok2 is not None:
        if blok2 == 1:
            BLOK = 'blok2'
    if blok3 is not None:
        if blok3 == 1:
            BLOK = 'blok3'
    if blok4 is not None:
        if blok4 == 1:
            BLOK = 'blok4'
    if blok5 is not None:
        if blok5 == 1:
            BLOK = 'blok5'
    if blok6 is not None:
        if blok6 == 1:
            BLOK = 'blok6'
    if blok7 is not None:
        if blok7 == 1:
            BLOK = 'blok7'

    if SEZONA == 'zima' and DAN == 'delavnik':
        if BLOK == 'blok1':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok2':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok3':
            rez = '%.4f €/kwh' % CENA1
            rez1 = '%.4f €/kw' % CENA6
            rez2 = '%.4f kw' % OBR_MOC1
        elif BLOK == 'blok4':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok5':
            rez = '%.4f €/kwh' % CENA1
            rez1 = '%.4f €/kw' % CENA6
            rez2 = '%.4f kw' % OBR_MOC1
        elif BLOK == 'blok6':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok7':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
    elif SEZONA == 'zima' and DAN == 'vikend':
        if BLOK == 'blok1':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
        elif BLOK == 'blok2':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok3':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok4':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok5':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok6':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok7':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
    elif SEZONA == 'vmes' and DAN == 'delavnik':
        if BLOK == 'blok1':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
        elif BLOK == 'blok2':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok3':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok4':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok5':
            rez = '%.4f €/kwh' % CENA2
            rez1 = '%.4f €/kw' % CENA7
            rez2 = '%.4f kw' % OBR_MOC2
        elif BLOK == 'blok6':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok7':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
    elif SEZONA == 'vmes' and DAN == 'vikend':
        if BLOK == 'blok1':
            rez = '%.4f €/kwh' % CENA5
            rez1 = '%.4f €/kw' % CENA10
            rez2 = '%.4f kw' % OBR_MOC5
        elif BLOK == 'blok2':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
        elif BLOK == 'blok3':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok4':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
        elif BLOK == 'blok5':
            rez = '%.4f €/kwh' % CENA3
            rez1 = '%.4f €/kw' % CENA8
            rez2 = '%.4f kw' % OBR_MOC3
        elif BLOK == 'blok6':
            rez = '%.4f €/kwh' % CENA4
            rez1 = '%.4f €/kw' % CENA9
            rez2 = '%.4f kw' % OBR_MOC4
        elif BLOK == 'blok7':
            rez = '%.4f €/kwh' % CENA5
            rez1 = '%.4f €/kw' % CENA10
            rez2 = '%.4f kw' % OBR_MOC5

    return (rez, rez1, rez2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0)


@app.callback(
    [
        Output('graph1', 'figure'),
        Output('button-izracun', 'n_clicks'),
        Output('cena-2t', 'children'),
        Output('cena-5t', 'children'),
    ],
    [
        Input('merilno-mesto-input', 'value'),
        Input('button-izracun', 'n_clicks')
    ],
)
def update_graph(merilno_mesto, clicks):
    global fig
    global CENA1, CENA2, CENA3, CENA4, CENA5
    global CENA6, CENA7, CENA8, CENA9, CENA10
    global OBR_MOC1, OBR_MOC2, OBR_MOC3, OBR_MOC4, OBR_MOC5

    if clicks is not None:
        if clicks == 1:

            # x = ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'avg', 'sep', 'okt', 'nov', 'dec']
            # y = np.random.randint(60, 90, 12)
            # y1 = np.random.randint(60, 90, 12)

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
            data = get_data(int(merilno_mesto))
            x = list(
                map(
                    lambda x: x[0] + " " + x[1],
                    list(
                        zip(
                            list(map(lambda x: month_map[x],
                                     data["ts_results"]["month_num"])),
                            list(map(lambda x: str(x), data["ts_results"]["year"]))))))

            y = np.sum([
                data["ts_results"]["omr_p"], data["ts_results"]["omr_mt"], data["ts_results"]["pens"], data["ts_results"]["omr_vt"]
            ],
                       axis=0)

            y1 = np.sum(
                [data["ts_results"]["new_omr_p"], data["ts_results"]["new_omr_e"], data["ts_results"]["new_pens"]],
                axis=0)

            fig = go.Figure(data=[
                go.Bar(x=x, y=y, name='2 tarifi', marker={'color': '#C32025'})
            ])
            fig.add_trace(
                go.Bar(x=x,
                       y=y1,
                       name='5 tarif',
                       marker={'color': 'rgb(145, 145, 145)'}))

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
                    'text': "2022",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                font_family="Inter, sans-serif",
                font_size=15,
            )

            fig.update_yaxes(zerolinecolor='rgba(0,0,0,0)')

            omreznine = np.add(data['tariff_prices']['tarife_prenos'],
                               data['tariff_prices']['tarife_distr'])
            moci = data['tariff_prices']['cene_moci']
            obr_moci = data['block_billing_powers']

            CENA1, CENA2, CENA3, CENA4, CENA5 = omreznine[0], omreznine[
                1], omreznine[2], omreznine[3], omreznine[4]
            CENA6, CENA7, CENA8, CENA9, CENA10 = moci[0], moci[1], moci[
                2], moci[3], moci[4]
            OBR_MOC1, OBR_MOC2, OBR_MOC3, OBR_MOC4, OBR_MOC5 = obr_moci[
                0], obr_moci[1], obr_moci[2], obr_moci[3], obr_moci[4]

            rez1 = '%.2f€' % np.sum(y)
            rez2 = '%.2f€' % np.sum(y1)

            return fig, 0, rez1, rez2
    return fig, 0, '0€', '0€'


if __name__ == '__main__':
    # run a cli command
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=False)
