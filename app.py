import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import (DashProxy, Input, MultiplexerTransform,
                                    Output, State)


from app_utils import *
from frontend import *
from settlement import Settlement
from utils import find_min_obr_p, handle_obr_moc


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

settlement = Settlement()

timeseries_data = None
tech_data = None
fig = create_empty_figure()

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

# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Store(id='session-ts-data', storage_type='session'),
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
    error_popup,
    mobile_view,
    header,
    dcc.Store(id='store-figure-data', storage_type='session'),
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


# Callback to update the graph
@app.callback(
    [
        Output('graph', 'figure'),
        Output('error-modal', 'is_open'),
        Output('error-modal-body', 'children'),
        Output('session-tech-data', 'data'),  # Updated to output to the store
        Output('session-results', 'data'),
        Output('output-data-upload', 'children'),
        Output('progress-bar-container', 'children'),
    ],
    [
        Input('button-izracun', 'n_clicks'),
        State('session-ts-data', 'data'),
        State('simulate', 'value'),
        State('pv-size', 'value'),
        State('session-tech-data', 'data'),
        State('session-results', 'data')
    ])
def main(n_clicks, session_ts_data, simulate_options, pv_size,
                 session_tech_data, session_results):
    # Initialize fig with an empty figure at the start
    fig = create_empty_figure()
    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate

    predlagane_obracunske_moci = session_tech_data.get('obr_p_values',
                                                     [None] * 5)
    try:
        prikljucna_moc = int(session_tech_data.get('prikljucna_moc', 0))
        uporabniska_skupina = session_tech_data.get('uporabniska_skupina', None)
    except:
        error = "Napaka pri vnosu tehničnih podatkov."
        return fig, True, error, session_tech_data, session_results, None, None

    session_tech_data["samooskrba"] = False
    session_tech_data["zbiralke"] = False
    if session_tech_data["checklist_values"] is not None:
        if " Net metering - Samooskrba" in session_tech_data["checklist_values"]:
            session_tech_data["samooskrba"] = True
        if " Meritve na zbiralkah" in session_tech_data["checklist_values"]:
            session_tech_data["zbiralke"] = True

    if uporabniska_skupina == None or prikljucna_moc == 0:
        error = "Napaka pri vnosu tehničnih podatkov."
        return fig, True, error, session_tech_data, session_results, None, None
    else:
        if prikljucna_moc > 43:
            if session_tech_data["obracunska_moc"] is None:
                error = "Napaka pri vnosu tehničnih podatkov."
                return fig, True, error, session_tech_data, session_results, None, None
        else:
            session_tech_data[
                "obracunska_moc"] = mapping_prikljucna_obracunska_moc[
                    prikljucna_moc]
        session_tech_data["obratovalne_ure"] = mapping_uporabniska_skupina[
            uporabniska_skupina][1]
        session_tech_data["consumer_type_id"] = mapping_uporabniska_skupina[
            uporabniska_skupina][0]
        session_tech_data["stevilo_faz"] = 1 if prikljucna_moc <= 8 else 3
        session_tech_data["trenutno_stevilo_tarif"] = 2

    min_obr_p = round(
        find_min_obr_p(1 if prikljucna_moc <= 8 else 3, prikljucna_moc), 1)

    calculate_obr_p_values = any(x is None for x in predlagane_obracunske_moci)
    if not calculate_obr_p_values:
        obr_p_correct = handle_obr_moc(predlagane_obracunske_moci,
                                       prikljucna_moc, min_obr_p)
        session_tech_data["obr_p_values"] = obr_p_correct

    if session_ts_data is not None:
        # SIMULATION OF THE ELEMENTS
        timeseries_data = pd.DataFrame(session_ts_data)
        timeseries_data, pv_size = simulate_additional_elements(timeseries_data,
                                                       simulate_options,
                                                       pv_size)

        # CALCULATE THE SETTLEMENT
        try:
            results = settlement.calculate_settlement(
                timeseries_data,
                session_tech_data,
                preprocess=True,
                calculate_obr_p_values=calculate_obr_p_values,
                override_year=True)
            session_tech_data["obr_p_values"] = results["block_billing_powers"]
        except Exception as e:
            error = "Napaka pri izračunu."
            return fig, True, error, session_tech_data, session_results, None, None

        # CREATE RESULTS FOR FRONTEND
        session_results = generate_results(results, session_results)

        # GENERATE GRAPHS
        fig = create_empty_figure()
        fig = update_fig(fig, results)

        return fig, False, None, session_tech_data, session_results, None, None
    else:
        fig = create_empty_figure()
        error = "Napaka pri nalaganju podatkov."
        return fig, True, error, session_tech_data, session_results, None, None


@app.callback([
    Output('predlagana-obracunska-moc-input1', 'value'),
    Output('predlagana-obracunska-moc-input2', 'value'),
    Output('predlagana-obracunska-moc-input3', 'value'),
    Output('predlagana-obracunska-moc-input4', 'value'),
    Output('predlagana-obracunska-moc-input5', 'value'),
], [
    Input('session-tech-data', 'data'),
])
def update_obr_p_input_fields(session_tech_data):
    if not session_tech_data['obr_p_values']:
        return [None, None, None, None, None]
    # Extract obr_p_x values
    obr_p_values = session_tech_data['obr_p_values']
    return obr_p_values


@app.callback(Output('session-tech-data', 'data'), [
    Input('predlagana-obracunska-moc-input1', 'value'),
    Input('predlagana-obracunska-moc-input2', 'value'),
    Input('predlagana-obracunska-moc-input3', 'value'),
    Input('predlagana-obracunska-moc-input4', 'value'),
    Input('predlagana-obracunska-moc-input5', 'value'),
    Input('prikljucna-moc', 'value'),
    Input('tip-odjemalca', 'value'),
    Input('check-list', 'value'),
    Input('pv-size', 'value'),
], [
    State('session-tech-data', 'data'),
],
              prevent_initial_call=True)
def update_store_from_inputs(obr_p_1, obr_p_2, obr_p_3, obr_p_4, obr_p_5,
                             prikljucna_moc, uporabniska_skupina,
                             checklist_values, pv_size, session_tech_data):
    session_tech_data["obr_p_values"] = [
        obr_p_1, obr_p_2, obr_p_3, obr_p_4, obr_p_5
    ]
    session_tech_data["prikljucna_moc"] = prikljucna_moc
    session_tech_data["uporabniska_skupina"] = uporabniska_skupina
    session_tech_data["checklist_values"] = checklist_values
    session_tech_data["pv_size"] = pv_size
    return session_tech_data


@app.callback([
    Output('omr2', 'children'),
    Output('omr5', 'children'),
    Output('energija-res', 'children'),
    Output('prispevki-res', 'children'),
], [
    Input('session-results', 'data'),
])
def update_results(session_tech_data):
    if not session_tech_data:
        return None, None, None, None
    omr2 = session_tech_data.get('omr2', 0)
    omr5 = session_tech_data.get('omr5', 0)
    energija = session_tech_data.get('energija-res', 0)
    prispevki = session_tech_data.get('prispevki-res', 0)
    return omr2, omr5, energija, prispevki


# Define the callback for uploading and displaying CSV data
@app.callback([
    Output('output-data-upload', 'children'),
    Output('session-ts-data', 'data'),
], [
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
])
def update_output(contents, filenames):
    if contents is None:
        raise PreventUpdate
    # Call parse_contents function and return its output
    content = contents[0]
    filename = filenames[0]

    output_data_upload, session_ts_data = parse_contents(content, filename)
    return output_data_upload, session_ts_data


@app.callback(Output('progress-bar-container',
                     'children'), [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_progress_bar(contents, filename):
    if contents is None:
        raise PreventUpdate

    # Simulate a progress bar; in a real app, this could be based on actual progress
    return html.Div("Nalaganje dokumenta...")


@app.callback([
    Output('progress-bar-container', 'style'),
    Output('output-data-upload', 'style'),
], [Input('hide-message-interval', 'n_intervals')])
def hide_upload_message(n):
    if n > 0:
        return {'display': 'none'}, {'display': 'none'}
    raise PreventUpdate


@app.callback(Output('obracunska-moc-input', 'children'),
              [Input('prikljucna-moc', 'value')],
              State('session-tech-data', 'data'),
              prevent_initial_call=True)
def update_extra_content(prikljucna_moc_value, session_tech_data):
    # Check if prikljucna_moc_value is not None and greater than 43
    if prikljucna_moc_value and prikljucna_moc_value > 43:
        return html.Div([
            dcc.Input(
                id='input-obracunska-moc',
                type='number',
                placeholder="Obračunska moc",
                className='prikljucna-moc-input',
            )
        ])
    else:
        return None


# fill obracunska moc to session_tech_data
@app.callback(
    Output('session-tech-data', 'data'),
    [Input('input-obracunska-moc', 'value')],
    State('session-tech-data', 'data'),
)
def update_obracunska_moc(obracunska_moc_value, session_tech_data):
    session_tech_data["obracunska_moc"] = obracunska_moc_value
    return session_tech_data


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


@app.callback(Output('button-izracun', 'disabled'),
              [Input('button-izracun', 'n_clicks')],
              prevent_initial_call=True)
def disable_button(n_clicks):
    return True  # Disable the button when it is clicked


@app.callback(Output('button-izracun', 'disabled'),
              [Input('session-results', 'data')],
              prevent_initial_call=True)
def enable_button(data):
    return False  # Re-enable the button after the data store is updated


# Run the app
if __name__ == '__main__':
    # app.run_server(debug=False, host="0.0.0.0", port=8080)
    app.run_server(debug=True)
