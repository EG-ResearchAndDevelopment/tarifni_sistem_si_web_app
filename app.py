import logging
import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (DashProxy, Input, MultiplexerTransform,
                                    Output, State)
from dash import callback_context

import time
import warnings
from app_utils import *
from frontend import *
from frontend import mapping_uporabniska_skupina
from settlement import Settlement
from utils import find_min_obr_p, handle_obr_moc, find_billing_powers

warnings.filterwarnings("ignore")
# Setup logging
logging.basicConfig(
    level= logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class ClosestKeyDict(dict):

    def __init__(self, mapping):
        super().__init__(mapping)
        # Prepare the keys as integers since they'll be compared numerically
        self.mapping = {int(k): v for k, v in mapping.items()}

    def __missing__(self, key):
        # Convert the key to integer for comparison, if it's not already one
        key = int(key)
        # Find the closest key
        closest_key = min(self.mapping.keys(), key=lambda k: abs(k - key))
        # Return the value associated with the closest key
        return self.mapping[closest_key]


# Define your mapping here
mapping_prikljucna_obracunska_moc = {
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
}

# Create an instance of your custom dictionary
mapping_prikljucna_obracunska_moc = ClosestKeyDict(
    mapping_prikljucna_obracunska_moc)

app = DashProxy(
    external_stylesheets=[dbc.themes.CYBORG, '/assets/mobile.css'],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,  # This is the line you need to add
    transforms=[MultiplexerTransform()],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.title = "Simulator tarifnega sistema"
server = app.server
fig = create_empty_figure()

# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Interval(id='clear-message-interval', interval=5000, n_intervals=0, disabled=True),
    dcc.Store(id='ts-data-path', storage_type='session', data={"filename": None, "data": None}),
    dcc.Store(id='ts-data', storage_type='session'),
    dcc.Store(id='obr-power-data', storage_type='session', data={
        'obr_p_values': [None, None, None, None, None],
    }),
    dcc.Store(id='tech-data',
              storage_type='session',
              data={
                  'obr_p_values': [None, None, None, None, None],
                  'prikljucna_moc': 0,
                  'obracunska_moc': 0,
                  'obratovalne_ure': None,
                  'uporabniska_skupina': None,
                  'consumer_type_id': 0,
                  'samooskrba': None,
                  'zbiralke': None,
                  'consumer_type_id': 0,
                  'stevilo_tarif': 2,
                  'stevilo_faz': None,
              }),
    dcc.Store(id='sim-data',
              storage_type='session',
              data={
                  'pv_size': 0,
                  'simulate_pv': False,
                  'simulate_hp': False,
              }),
    dcc.Store(id='res-data',
              storage_type='session',
              data={
                  "omr2": 0,
                  "omr5": 0,
                  "energija": 0,
                  "prispevki": 0
              }),
    error_popup,
    mobile_view,
    header,
    # dcc.Store(id='store-figure-data', storage_type='session'),
    html.Div(
        children=[
            html.Div(id='background-div',
                     className='background-div',
                     children=[
                         dcc.Graph(id='graph',
                                   className='mesecni-graf',
                                   figure=fig,
                                   config={'displayModeBar': False}),
                     ]),
            dialog,
            omreznina_nova,
            omreznina_stara,
            # vertical black line
            html.Div(className='vertical-line'),
            energija,
            prispevki,
        ],
        className="hide-on-mobile",
    ),
    footer,
])


@app.callback(
    [
        Output('graph', 'figure'),
        Output('error-modal', 'is_open'),
        Output('error-modal-body', 'children'),
        Output('res-data', 'data'),
        Output('tech-data', 'data'),
        Output('obr-power-data', 'data')
    ],
    [
        Input('button-izracun', 'n_clicks'),
    ],
    [
        State('ts-data', 'data'),
        State('tech-data', 'data'),
        State('sim-data', 'data'),
        State('obr-power-data', 'data'),
    ],
)
def main(n_clicks, ts_data, tech_data, sim_data, obr_power_data):
    res_data = {
                  "omr2": 0,
                  "omr5": 0,
                  "energija": 0,
                  "prispevki": 0
              }
    fig = create_empty_figure()
    if n_clicks is None:
        raise PreventUpdate
    check, error = check_if_tech_is_populated(tech_data)
    if not check:
        error_message = f"Izpolni polje: {error}"
        return fig, True, error_message, res_data, tech_data, obr_power_data
    
    prikljucna_moc = tech_data["prikljucna_moc"]

    if ts_data is None:
        return fig, True, "Najprej je potrebno naložiti podatke.", res_data, tech_data, obr_power_data
    
    timeseries_data = pd.DataFrame(ts_data)
    timeseries_data = simulate_additional_elements(
        timeseries_data, sim_data)
    min_obr_p = round(find_min_obr_p(tech_data["stevilo_faz"], prikljucna_moc), 1)
    
    # if any of the values is None then calculate the values based on the proposed approach
    if any([x is None for x in obr_power_data["obr_p_values"]]):
        obr_power_data["obr_p_values"] = find_billing_powers(timeseries_data, tech_data, find_optimal=False)

    obr_p_correct = handle_obr_moc(obr_power_data["obr_p_values"],
                                    prikljucna_moc, min_obr_p)

    obr_power_data["obr_p_values"] = obr_p_correct
    logging.debug(f"Corrected operational powers: {obr_p_correct}")

    logging.info("Simulation of additional elements completed.")

    technical_data = {
        "consumer_type_id": tech_data["consumer_type_id"],
        "uporabniska_skupina": tech_data["uporabniska_skupina"],
        "obr_p_values": obr_power_data["obr_p_values"],
        "prikljucna_moc": prikljucna_moc,
        "obracunska_moc": tech_data["obracunska_moc"],
        "samooskrba": tech_data["samooskrba"],
        "zbiralke": tech_data["zbiralke"],
        "stevilo_faz": tech_data["stevilo_faz"],
        "stevilo_tarif": tech_data["stevilo_tarif"],
        "obratovalne_ure": tech_data["obratovalne_ure"],
    }
    try:
        start = time.time()
        settlement = Settlement()
        logging.info("Starting settlement calculation.")
        results = settlement.calculate_settlement(
            timeseries_data,
            technical_data,
            preprocess=True,
            override_year=True)
        logging.info("Settlement calculation completed.")
        end = time.time()
        logging.info(f"Settlement calculation completed in {end - start} seconds.")
        logging.info(f"Results: {results}")
        # tech_data["obr_p_values"] = results["block_billing_powers"]
    except Exception as e:
        logging.error(f"Error during settlement calculation: {e}")
        return fig, True, "Napaka pri izračunu, vaš primer bomo obravnavali v najkrajšem možnem času.", res_data, tech_data, obr_power_data
    obr_power_data["obr_p_values"] = results["block_billing_powers"]
    # CREATE RESULTS FOR FRONTEND
    res_data = generate_results(results)
    
    # GENERATE GRAPHS
    fig = create_empty_figure()
    fig = update_fig(fig, results)

    return fig, False, None, res_data, tech_data, obr_power_data


def check_if_tech_is_populated(tech_data):
    if tech_data['prikljucna_moc'] is None:
        return False, "Priključna moč"
    if tech_data['obracunska_moc'] is None:
        return False, "Obracunska moč"
    if tech_data['uporabniska_skupina'] is None:
        return False, "Uporabniška skupina"
    return True, None

@app.callback(
    [
        Output('sim-data', 'data'),
    ],
    [
        Input('pv-size', 'value'),
        Input('simulate-options', 'value'),
    ],
    [
        State('sim-data', 'data'),
    ],
)
def update_sim(pv_size, simulate_options, sim_data):
    if simulate_options is None:
        sim_data["simulate_pv"] = False
        sim_data["simulate_hp"] = False
        return sim_data
    sim_data["simulate_pv"] = " Simuliraj novo sončno elektrarno" in simulate_options
    sim_data["simulate_hp"] = " Simuliraj novo toplotno črpalko" in simulate_options
    if pv_size is None:
        sim_data["pv_size"] = 0
    sim_data["pv_size"] = pv_size
    return sim_data

@app.callback(
    [
        Output('tech-data', 'data'),
    ],
    [
        Input('prikljucna-moc', 'value'),
        Input('obracunska-moc', 'value'),
        Input('tip-odjemalca', 'value'),
        Input('check-list', 'value'),
    ],
    [
        State('tech-data', 'data'),
    ],
)
def update_tech_data(prikljucna_moc, obracunska_moc, uporabniska_skupina, izbirni_seznam, tech_data):
    if prikljucna_moc is None:
        tech_data['prikljucna_moc'] = None
        return tech_data
    prikljucna_moc = int(prikljucna_moc)
    tech_data['prikljucna_moc'] = prikljucna_moc
    tech_data["stevilo_faz"] = 1 if prikljucna_moc <= 8 else 3
    if uporabniska_skupina is None:
        tech_data['uporabniska_skupina'] = None
        return tech_data
    tech_data['uporabniska_skupina'] = uporabniska_skupina
    tech_data["obratovalne_ure"] = mapping_uporabniska_skupina[uporabniska_skupina][1]
    tech_data["consumer_type_id"] = mapping_uporabniska_skupina[uporabniska_skupina][0]
    if prikljucna_moc > 43:
        print("prikljucna_moc > 43")
        # set obracunska_moc to obracunska_moc
        tech_data['obracunska_moc'] = obracunska_moc
    else:
        tech_data["obracunska_moc"] = mapping_prikljucna_obracunska_moc[prikljucna_moc]
    if izbirni_seznam is None:
        return tech_data
    tech_data["samooskrba"] = " Net metering - Samooskrba" in izbirni_seznam
    tech_data["zbiralke"] = " Meritve na zbiralkah" in izbirni_seznam
    return tech_data

@app.callback(
    [
        Output('omr2', 'children'),
        Output('omr5', 'children'),
        Output('energija', 'children'),
        Output('prispevki', 'children'),
    ],
    [
        Input('res-data', 'data'),
    ],
    prevent_initial_call=True
)
def update_results(res_data):
    omr2 = res_data['omr2']
    omr5 = res_data['omr5']
    energija = res_data['energija']
    prispevki = res_data['prispevki']
    return omr2, omr5, energija, prispevki


@app.callback([
        Output('output-data-upload', 'children'),
        Output('ts-data-path', 'data'),
        Output('res-data', 'data'),
        Output('tech-data', 'data'),
        Output('prikljucna-moc', 'value'),
        Output('obracunska-moc', 'children'),
        Output('tip-odjemalca', 'value'),
        Output('obr-power-data', 'data'),
    ],
    [
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('ts-data-path', 'data'),
    ],
    prevent_initial_call=True
)
def update_and_reset_output(contents, filename, current_filename):
    if contents is None or current_filename["filename"]==filename:
        raise PreventUpdate
    
    results = {"omr2": "0€", "omr5": "0€", "energija": "0€", "prispevki": "0€"}
    tech_data = {
        'obr_p_values': [None, None, None, None, None],
        'prikljucna_moc': None,
        'obracunska_moc': None,
        'obratovalne_ure': None,
        'uporabniska_skupina': None,
        'consumer_type_id': 0,
        'samooskrba': False,
        'zbiralke': False,
        'stevilo_tarif': 2,
        'stevilo_faz': None,
    }
    obr_power_data = {
        'obr_p_values': [None, None, None, None, None],
    }
    current_filename["filename"] = filename
    current_filename["data"] = contents
    return html.Div(['Dokument uspešno naložen.']), current_filename, results, tech_data, None, None, None, obr_power_data

@app.callback(
    [
        Output('obracunska-moc', 'children'),
    ],
    [
        Input('prikljucna-moc', 'value'),
    ],
    prevent_initial_call=True
)
def update_obracunska_moc(prikljucna_moc):
    if prikljucna_moc is None:
        return [0]
    prikljucna_moc = int(prikljucna_moc)
    if prikljucna_moc > 43:
        return [html.Div(children=[
            # html.P("Obstoječe stanje:", ),
            dcc.Input(placeholder='obracunska moč',
                      type="number",
                      value='',
                      className='obracunska-moc',
                      id='obracunska-moc',
            ),
        ])
        ]
    else:
        return None

@app.callback([
        Output('output-data-upload', 'children'),
        Output('ts-data', 'data'),
        Output('clear-message-interval', 'disabled'),  # Add this output
    ],
    [
        Input('ts-data-path', 'data'),
    ],
    prevent_initial_call=True
)
def parse_data(ts_data_path):
    contents = ts_data_path["data"]
    filename = ts_data_path["filename"]
    start = time.time()
    logging.info("Starting data parsing.")
    output_data_upload, ts_data = parse_contents(contents, filename)
    logging.info("Data parsing completed.")
    end = time.time()
    logging.info(f"Data parsing completed in {end - start} seconds.")
    # Trigger the interval to start counting down
    return output_data_upload, ts_data, False  # Set 'disabled' to False to start the interval

@app.callback(
    [
        Output('output-data-upload', 'children'),
        Output('clear-message-interval', 'disabled'),
        Output('clear-message-interval', 'n_intervals'),
    ],
    [Input('clear-message-interval', 'n_intervals')],
    prevent_initial_call=True
)
def clear_message(n_intervals):
    # Clear the message, disable the interval, reset n_intervals
    return '', True, 0


@app.callback([
        Output('predlagana-obracunska-moc1', 'value'),
        Output('predlagana-obracunska-moc2', 'value'),
        Output('predlagana-obracunska-moc3', 'value'),
        Output('predlagana-obracunska-moc4', 'value'),
        Output('predlagana-obracunska-moc5', 'value'),
    ],
    [
        Input('obr-power-data', 'data'),
    ],
    prevent_initial_call=True
)
def update_obr_p_input(obr_power_data):
    if not obr_power_data['obr_p_values']:
        return [None, None, None, None, None]
    # Extract obr_p_x values
    obr_p_values = obr_power_data['obr_p_values']
    return obr_p_values

@app.callback([
        Output('obr-power-data', 'data'),
    ],
    [
        Input('predlagana-obracunska-moc1', 'value'),
        Input('predlagana-obracunska-moc2', 'value'),
        Input('predlagana-obracunska-moc3', 'value'),
        Input('predlagana-obracunska-moc4', 'value'),
        Input('predlagana-obracunska-moc5', 'value'),
    ],
    [
        State('obr-power-data', 'data')
    ],
    prevent_initial_call=True
)
def update_obr_p_input(obr_1, obr_2, obr_3, obr_4, obr_5, obr_power_data):
    obr_power_data["obr_p_values"] = [obr_1, obr_2, obr_3, obr_4, obr_5]
    return obr_power_data

@app.callback([
        Output('obr-power-data', 'data'),
    ], 
    [Input('button-izracun-optimalnih-moci-1', 'n_clicks')], 
    [
        State('ts-data', 'data'),
        State('tech-data', 'data'),
        State('sim-data', 'data'),
    ],
    prevent_initial_call=True
)
def calculate_optimal_obr_p(n_clicks, ts_data, tech_data, sim_data):
    if n_clicks is None:
        raise PreventUpdate
    timeseries_data = pd.DataFrame(ts_data)
    timeseries_data = simulate_additional_elements(
            timeseries_data, sim_data)

    obr_p = find_billing_powers(timeseries_data, tech_data, find_optimal=True)
    obr_p = np.round(obr_p, 2)
    # add this here
    obr_power_data = {
        'obr_p_values': obr_p,
    }
    return obr_power_data

@app.callback(Output('proposed-power-inputs', 'style'),
              [Input('button-izracun', 'n_clicks')])
def show_inputs(n_clicks):
    if not callback_context.triggered:
        # If nothing triggered the callback, don't do anything
        raise PreventUpdate
    if n_clicks != 0:
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output("pomoc-modal", "is_open"),  # Adjusted to correct modal ID
    [Input("open", "n_clicks"),
     Input("close", "n_clicks")],
    [State("pomoc-modal", "is_open")],  # Adjusted to correct modal ID
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)