import base64
import io
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import time
import dash_bootstrap_components as dbc


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ', html.A('Select Files')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=True
    ),
    html.Div(id='progress-bar-container', children=[
        # This Div will be used to show/hide a simulated progress bar
    ]),
    html.Div(id='output-data-upload'),
])

@app.callback(
    Output('progress-bar-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_progress_bar(contents, filename):
    if contents is None:
        raise dash.exceptions.PreventUpdate

    # Simulate a progress bar; in a real app, this could be based on actual progress
    return html.Div(children=[
        html.Div("Uploading..."),
        dbc.Progress(value=50, max=100)  # Example: halfway done
    ])

@app.callback(
    Output('output-data-upload', 'children'),
    # Output('progress-bar-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'), State('upload-data', 'last_modified')]
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        time.sleep(2)
        children = [
            html.Div([
                html.H5(list_of_names),
                html.H6("File uploaded successfully."),
            ])
        ]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)
