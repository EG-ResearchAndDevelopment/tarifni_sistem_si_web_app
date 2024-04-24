import dash_bootstrap_components as dbc
from dash import dcc, html
# import dash_uploader as du


header = html.Div(
    children=[
        html.Div(
            id='header-div',
            className='header-div',
            children=[
                html.Img(className='logo', src="./assets/images/logo-60.svg"),
                html.Div(
                    children=[
                        html.Div(
                            className='help-div',
                            children=[
                                dbc.Button("Pomoč",
                                           id="open",
                                           className="button-izracun",
                                           n_clicks=0),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(
                                            dbc.ModalTitle("Pomoč")),
                                        dbc.ModalBody(
                                            "Merilni podatki morajo biti v naslednji obliki:"
                                        ),
                                        html.Img(
                                            src="./assets/images/primer.jpg"),
                                        dbc.ModalBody(
                                            "V excel datoteki so lahko prisotni tudi drugi stolpci, je pa pomembno, da so prisotni vsaj ti stolpci, ki so prikazani na sliki. V primeru, da so prisotni tudi drugi stolpci, se bodo ti ignorirali."
                                        ),
                                        dbc.ModalFooter(
                                            dbc.Button(
                                                "Close",
                                                id="close",
                                                className="button-izracun",
                                                n_clicks=0)),
                                    ],
                                    id="pomoc-modal",
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
)

error_popup = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Error")),
        dbc.ModalBody(id="error-modal-body"),
    ],
    id="error-modal",
    is_open=False,
)

mobile_view = html.Div(
    children=[
        html.Div(id="mobile-header-div",
                 className="mobile-header-div",
                 children=[
                     html.Img(className="logo",
                              src="./assets/images/logo-60.svg",
                              style={'margin-bottom': '20px'}),
                 ]),
        html.
        P('Simulator tarifnega sistema deluje le na računalniku. Glavni razlog, je uvažanje podatkov iz excel datoteke.'
          )
    ],
    className="show-on-mobile",
)

header = html.Div(
    children=[
        html.Div(
            id='header-div',
            className='header-div',
            children=[
                html.Img(className='logo', src="./assets/images/logo-60.svg"),
                html.Div(
                    children=[
                        html.Div(
                            className='help-div',
                            children=[
                                dbc.Button("Pomoč",
                                           id="open",
                                           className="button-izracun",
                                           n_clicks=0),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(
                                            dbc.ModalTitle("Pomoč")),
                                        dbc.ModalBody(
                                            "Merilni podatki morajo biti v naslednji obliki:"
                                        ),
                                        html.Img(
                                            src="./assets/images/primer.jpg"),
                                        dbc.ModalBody(
                                            "V excel datoteki so lahko prisotni tudi drugi stolpci, je pa pomembno, da so prisotni vsaj ti stolpci, ki so prikazani na sliki. V primeru, da so prisotni tudi drugi stolpci, se bodo ti ignorirali."
                                        ),
                                        dbc.ModalFooter(
                                            dbc.Button(
                                                "Close",
                                                id="close",
                                                className="button-izracun",
                                                n_clicks=0)),
                                    ],
                                    id="pomoc-modal",
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
)

footer = html.Div(
    children=[
        html.Div(
            className='footer-div',
            children=[
                html.Div(
                    children=[
                        html.
                        P("© 2024 Elektro Gorenjska d.d. Vse pravice pridržane. Vse informacije so informativne narave."
                          ),
                        html.
                        P("Informacija o ceni po novem tarifnem sistemu je izključno informativne narave ter ne predstavlja pravno zavezujočega dokumenta ali izjave družbe Elektro Gorenjska, d. d.. Na podlagi te informacije ne nastanejo nikakršne obveznosti ali pravice, niti je ni mogoče uporabiti v katerem koli postopku uveljavljanja ali dokazovanja morebitnih pravic ali zahtevkov. Elektro Gorenjska, d. d. ne jamči ali odgovarja za vsebino, pravilnost ali točnost informacije. Uporabnik uporablja prejeto informacijo na lastno odgovornost in je odgovornost družbe Elektro Gorenjska, d. d. za kakršno koli neposredno ali posredno škodo, stroške ali neprijetnosti, ki bi lahko nastale uporabniku zaradi uporabe te informacije, v celoti izključena."
                          ),
                    ],
                    className="disclaimer",
                ),
            ],
        ),
    ],
    className="hide-on-mobile",
)

prispevki = html.Div(
    id='prispevki-top-div',
    className='prispevki-top-div',
    children=[
        html.Div(className='main',
                 children=[
                     html.Div(children=[
                         html.H5('PRISPEVKI'),
                         html.H4(id='prispevki-res', children=['0€']),
                         html.P("Vse cene vključujejo DDV", style={'fontSize': 'small'})
                     ])
                 ]),
        html.Div(className='bubble',
                 children=[html.Img(src='./assets/images/icon_prispevki.svg')
                           ]),
        html.Div(className='bubble2'),
    ])

energija = html.Div(
    id='energija-top-div',
    className='energija-top-div',
    children=[
        html.Div(className='main',
                 children=[
                     html.Div(children=[
                         html.H5('ENERGIJA'),
                         html.H4(id='energija-res', children=['0€']),
                     ])
                 ]),
        html.Div(className='bubble',
                 children=[html.Img(src='./assets/images/icon_energija.svg')]),
        html.Div(className='bubble2'),
    ])
omreznina_stara = html.Div(
    id='omreznina-top-div',
    className='omreznina-top-div',
    children=[
        html.Div(className='main',
                 children=[
                     html.Div(children=[
                         html.H5('OMREŽNINA DANES'),
                         html.H4(id='omr2', children=['0€']),
                     ])
                 ]),
        html.Div(className='bubble',
                 children=[html.Img(src='./assets/images/icon_share.svg')]),
        html.Div(className='bubble2'),
    ])

omreznina_nova = html.Div(
    id='omreznina1-top-div',
    className='omreznina1-top-div',
    children=[
        html.Div(className='main',
                 children=[
                     html.Div(children=[
                         html.H5('OMREŽNINA PO NOVEM'),
                         html.H4(id='omr5', children=['0€']),
                     ])
                 ]),
        html.Div(className='bubble',
                 children=[html.Img(src='./assets/images/icon_share.svg')]),
        html.Div(className='bubble2'),
    ])

mapping_uporabniska_skupina = {
    "gospodinjski odjem": [1, 0],
    "NN brez merjene moči": [2, 0],
    "NN z merjeno močjo - T >= 2500ur": [3, 2500],
    "NN z merjeno močjo - T < 2500ur": [3, 0],
    "SN - T >= 2500ur": [4, 2500],
    "SN - T < 2500ur": [4, 0],
}

omrezninski_vhodni_podatki = html.Div(
    className='column',
    style={
        'flex': 1,
        'padding-right': '80px'
    },
    children=[
        html.Div(
            [
                html.
                P("Naloži podatke o porabi v formatu MojElektro (gumb POMOČ):",
                  ),
                dcc.Upload(id='upload-data',
                           className='upload-data',
                           children=html.Div(
                               [html.P('Izberi datoteko: 15 min podatki')]),
                           multiple=False),
                # html.Div([
                #     du.Upload(id='upload-data',
                #               text='Izberi datoteko: 15 min podatki',
                #            text_completed='Datoteka naložena: ',
                #            default_style={
                #                  'width': '100%',
                #                  'height': '60px',
                #                  'lineHeight': '60px',
                #                  'color': 'black',
                #             },
                #            ),
                #     ], 
                #     className='upload-data-new'),
                html.Div(
                    id='progress-bar-container',
                    className='text',
                    children=[
                        # This Div will be used to show/hide a simulated progress bar
                    ]),
                html.Div(id='output-data-upload'),
                # horisontal line black
                html.Div(
                    className='line',
                    children=[
                        html.Hr(),
                    ],
                ),
                html.P("Vstavi priključno moč:", ),
                dcc.Input(
                    placeholder='priključna moč',
                    type="number",
                    value='',
                    className='prikljucna-moc-input',
                    id='prikljucna-moc',
                ),
                html.Div(id='obracunska-moc-input'),
                dcc.Dropdown(list(mapping_uporabniska_skupina.keys()),
                             'Izberi uporabniško skupino:',
                             className='dropdown',
                             placeholder='Izberi uporabniško skupino',
                             id='tip-odjemalca'),
                html.Div(children=[
                    html.P("Obstoječe stanje:", ),
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
            ],
            style={
                'margin-top': '20px',
                'margin-bottom': '30px',
            }),
        # hide this at the begining after the calculation was succesful show it, so that the consumer can change it
        html.Div(id='proposed-power-inputs',
                 style={'display': 'none'},
                 children=[
                     html.P('Po želji spreminjaj predlagane obračunske moči:'),
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
                 ]),
    ])

simulacijski_vhodni_podatki = html.Div(
    className='column',
    style={
        'flex': 1,
        'padding-left': '80px'
    },
    children=[
        html.Div(
            className='line',
            children=[
                html.Hr(),
            ],
        ),
        html.Div(children=[
            html.P('Simulacije (OPCIJSKO):'),
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
                                    children='Izračun',
                                    n_clicks=0,
                                    disabled=False)
                    ],
                    type="circle"),
    ])

dialog = html.Div(
    className='dialog-div',
    children=[
        omrezninski_vhodni_podatki,
        simulacijski_vhodni_podatki,
    ],
    style={
        'display': 'flex',
        'flexDirection': 'row'
    },
)
