import datetime
import json

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from consmodel import HP, PV
from dash import dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Dash, Input, Output, State
from plotly.utils import PlotlyJSONEncoder

from app_utils import *
from frontend import *
from settlement import Settlement
from utils import find_min_obr_p, handle_prikljucna_moc

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
    "69": 69,
    "86": 86,
    "110": 110,
    "138": 138,
}
# Create an instance of your custom dictionary
mapping_prikljucna_obracunska_moc = ClosestKeyDict(
    mapping_prikljucna_obracunska_moc)

settlement = Settlement()
timeseries_data = None
tech_data = None
fig = create_empty_figure()

app = Dash(
    external_stylesheets=[dbc.themes.CYBORG, '/assets/mobile.css'],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,  # This is the line you need to add
    # transforms=[MultiplexerTransform()],
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }],
)
app.title = "Simulator tarifnega sistema"
server = app.server

# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Store(id='session-tsdata', storage_type='session'),
    dcc.Store(id='session-tech-data',
              storage_type='session',
              data={
                  'obr_p_values': [None, None, None, None, None],
                  'prikljucna_moc': None,
                  'obracunska_moc': None,
                  'obratovalne_ure': None,
                  'consumer_type_id': None,
                  'samooskrba': None,
                  'zbiralke': None,
                  'trenutno_stevilo_tarif': 2,
                  'stevilo_faz': None
              }),
    dcc.Store(id='session-results',
              storage_type='session',
              data={
                  "omr2": 0,
                  "omr5": 0,
                  "energija": 0,
                  "prispevki": 0
              }),
    dcc.Store(id='store-figure-data', storage_type='session'),
    # dcc.Store(
    error_popup,
    mobile_view,
    header,
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
            energija,
            prispevki,
        ],
        className="hide-on-mobile",
    ),
    footer,
])


# Callback to update the graph
@app.callback(
    [
        Output('graph', 'figure'),
        Output('error-modal', 'is_open'),
        Output('error-modal-body', 'children'),
        Output('session-tech-data', 'data'),  # Updated to output to the store
        Output('session-results', 'data'),
    ],
    [
        Input('button-izracun', 'n_clicks'),
        State('session-tsdata',
              'data'),  # Assuming you store your data in 'session-tsdata'
        State('simulate', 'value'),
        State('pv-size', 'value'),
        State('session-tech-data', 'data'),
        State('session-results', 'data')
    ])
def update_graph(n_clicks, session_data, simulate_options, pv_size, tech_data_store,
                 session_results):
    # If the button is not clicked, do not update the graph
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate

    # Extract obr_p_x values from the store
    predlagane_obracunske_moci = tech_data_store.get(
        'obr_p_values', [None] * 5)  # Defaults to None if not found
    prikljucna_moc = tech_data_store.get('prikljucna_moc', None)
    tip_odjemalca = tech_data_store.get('tip_odjemalca', None)
    calculate_obr_p_values = any(x is None for x in predlagane_obracunske_moci)

    tech_data_store["samooskrba"] = False
    tech_data_store["zbiralke"] = False
    if tech_data_store["checklist_values"] is not None:
        if " Net metering - Samooskrba" in tech_data_store["checklist_values"]:
            tech_data_store["samooskrba"] = True
        if " Meritve na zbiralkah" in tech_data_store["checklist_values"]:
            tech_data_store["zbiralke"] = True

    if tip_odjemalca == None:
        fig = create_empty_figure()
        error = "Napaka pri vnosu tehničnih podatkov."
        return fig, True, error, tech_data_store, session_results
    if prikljucna_moc == None:
        error = "Napaka pri vnosu tehničnih podatkov."
        fig = create_empty_figure()
        return fig, True, error, tech_data_store, session_results
    else:
        if prikljucna_moc > 43:
            if tech_data_store["obracunska_moc"] is None:
                error = "Napaka pri vnosu tehničnih podatkov."
                fig = create_empty_figure()
                return fig, True, error, tech_data_store, session_results
        else:
            tech_data_store["obracunska_moc"] = mapping_prikljucna_obracunska_moc[
                prikljucna_moc]
        tech_data_store["obratovalne_ure"] = mapping_tip_odjemalca[
            tip_odjemalca][1]
        tech_data_store["consumer_type_id"] = mapping_tip_odjemalca[
            tip_odjemalca][0]
        tech_data_store["stevilo_faz"] = 1 if int(prikljucna_moc) <= 8 else 3
        tech_data_store["trenutno_stevilo_tarif"] = 2
    print(tech_data_store)
    min_obr_p = round(
        find_min_obr_p(1 if int(prikljucna_moc) <= 8 else 3, prikljucna_moc),
        1)

    if not calculate_obr_p_values:
        obr_p_correct = handle_prikljucna_moc(predlagane_obracunske_moci,
                                              min_obr_p)
        tech_data_store["obr_p_values"] = obr_p_correct

    if session_data is not None:
        timeseries_data = pd.DataFrame(session_data)
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
        if simulate_options is not None:
            if " Simuliraj sončno elektrarno" in simulate_options:
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
            if " Simuliraj toplotno črpalko" in simulate_options:
                hp = HP(lat, lon, alt)
                hp_timeseries = hp.simulate(22.0,
                                            start=start,
                                            end=end,
                                            freq='15min')
                # difference between the two timeseries
                timeseries_data[
                    "p"] = timeseries_data["p"] + hp_timeseries.values
        try:

            settlement.calculate_settlement(
                0,
                timeseries_data,
                tech_data_store,
                calculate_obr_p_values=calculate_obr_p_values,
                override_year=False)
            data = settlement.output
            tech_data_store["obr_p_values"] = data["block_billing_powers"]
        except:
            error = "Napaka pri izračunu."
            return fig, True, error, tech_data_store, session_results

        omr_old = np.sum([
            data["ts_results"]["omr_p"], data["ts_results"]["omr_mt"],
            data["ts_results"]["pens"], data["ts_results"]["omr_vt"]
        ],
                         axis=0)

        omr_new = np.sum([
            data["ts_results"]["new_omr_p"], data["ts_results"]["new_omr_e"],
            data["ts_results"]["new_pens"]
        ],
                         axis=0)
        # Initialize the Dash app with Bootstrap
        fig = create_empty_figure()
        fig = update_fig(fig, data)
        # figure_json = json.dumps(fig, cls=PlotlyJSONEncoder)

        omr2_res = '%.2f€' % np.sum(omr_old)
        omr5_res = '%.2f€' % np.sum(omr_new)
        energy_res = '%.2f€' % np.sum(data["ts_results"]["e_mt"] +
                                      data["ts_results"]["e_vt"])
        prispevki_res = '%.2f€' % np.sum(data["ts_results"]["ove_spte_p"] +
                                         data["ts_results"]["ove_spte_e"])
        session_results.update({
            "omr2": omr2_res,
            "omr5": omr5_res,
            "energija-res": energy_res,
            "prispevki-res": prispevki_res
        })

        return fig, False, None, tech_data_store, session_results
    else:
        error = "Napaka pri nalaganju podatkov."
        return fig, True, error, tech_data_store, session_results


@app.callback(
    [
        Output('predlagana-obracunska-moc-input1', 'value'),
        Output('predlagana-obracunska-moc-input2', 'value'),
        Output('predlagana-obracunska-moc-input3', 'value'),
        Output('predlagana-obracunska-moc-input4', 'value'),
        Output('predlagana-obracunska-moc-input5', 'value'),
    ],
    [
        Input('session-tech-data',
              'data'),  # Triggered by updates in store data
    ]
)
def update_obr_p_input_fields(store_data):
    # Default to not display if there's no data or specific condition not met
    if not store_data['obr_p_values']:
        return [None, None, None, None, None]  # Keep hidden if no data

    # Extract obr_p_x values
    obr_p_values = store_data['obr_p_values']

    # Return the updated values and visibility
    return obr_p_values


@app.callback(
    Output('session-tech-data',
           'data'),  # Target the data property of the store
    [
        Input('predlagana-obracunska-moc-input1',
              'value'),  # Trigger for each input
        Input('predlagana-obracunska-moc-input2', 'value'),
        Input('predlagana-obracunska-moc-input3', 'value'),
        Input('predlagana-obracunska-moc-input4', 'value'),
        Input('predlagana-obracunska-moc-input5', 'value'),
        Input('prikljucna-moc', 'value'),
        Input('tip-odjemalca', 'value'),
        Input('check-list', 'value'),
    ],
    [
        State('session-tech-data', 'data'),  # Get the current store data
    ])
def update_store_from_inputs(obr_p_1, obr_p_2, obr_p_3, obr_p_4, obr_p_5, prikljucna_moc, tip_odjemalca, checklist_values,
                             store_data):
    # Update the store with new values from inputs
    # get current store data
    store_data["obr_p_values"] = [obr_p_1, obr_p_2, obr_p_3, obr_p_4, obr_p_5]
    store_data["prikljucna_moc"] = prikljucna_moc
    store_data["tip_odjemalca"] = tip_odjemalca
    store_data["checklist_values"] = checklist_values


    return store_data

#update results from store-results
@app.callback(
    [
        Output('omr2', 'children'),
        Output('omr5', 'children'),
        Output('energija-res', 'children'),
        Output('prispevki-res', 'children'),
    ],
    [
        Input('session-results',
              'data'),  # Triggered by updates in store data
    ]
)
def update_results(store_data):
    # Default to not display if there's no data or specific condition not met
    if not store_data:
        return [None, None, None, None]
    
    # Extract obr_p_x values
    omr2 = store_data.get('omr2', 0)
    omr5 = store_data.get('omr5', 0)
    energija = store_data.get('energija-res', 0)
    prispevki = store_data.get('prispevki-res', 0)

    # Return the updated values and visibility
    return omr2, omr5, energija, prispevki


# Define the callback for uploading and displaying CSV data
@app.callback([
    Output('output-data-upload', 'children'),
    Output('session-tsdata', 'data'),
    ], 
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
    ]
)
def update_output(contents, filenames):
    if contents is not None:
        # Call parse_contents function and return its output
        content = contents[0]
        filename = filenames[0]
        return parse_contents(content, filename)

    # If there's no content, prevent update
    return (None, dash.no_update)

@app.callback(
    Output('obracunska-moc-input', 'children'),
    [Input('prikljucna-moc', 'value')],
    State('session-tech-data', 'data'),
    prevent_initial_call=True
)
def update_extra_content(prikljucna_moc_value, tech_data):
    # Check if prikljucna_moc_value is not None and greater than 43
    if prikljucna_moc_value and prikljucna_moc_value > 43:
        return html.Div([
            # html.P("Priključna moč presega 43. Prosimo, vnesite obracunsko moc:"),
            dcc.Input(id='input-obracunska-moc', type='number', placeholder="Obracunska moc", className='prikljucna-moc-input',)
        ])
    else:
        return None

# fill obracunska moc to tech_data
@app.callback(
    Output('session-tech-data', 'data'),
    [Input('input-obracunska-moc', 'value')],
    State('session-tech-data', 'data'),
)
def update_obracunska_moc(obracunska_moc_value, tech_data):
    tech_data["obracunska_moc"] = obracunska_moc_value
    return tech_data

@app.callback(Output('proposed-power-inputs', 'style'),
              [Input('button-izracun', 'n_clicks')])
def show_inputs(n_clicks):
    if n_clicks != 0:
        return {'display': 'block'}
    return {'display': 'none'}


# Adjusted Callback to toggle the help modal on and off
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
