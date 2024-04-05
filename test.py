import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import random

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Click me", id="trigger-button", n_clicks=0),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Error")),
            dbc.ModalBody(id="error-modal-body"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-error-modal", className="ml-auto")
            ),
        ],
        id="error-modal",
        is_open=False,
    )
])

@app.callback(
    [Output("error-modal", "is_open"),
     Output("error-modal-body", "children")],
    [Input("trigger-button", "n_clicks"),
     Input("close-error-modal", "n_clicks")],
    [State("error-modal", "is_open")]
)
def toggle_modal(trigger_n_clicks, close_n_clicks, is_open):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "trigger-button":
        # Simulate an operation that might fail
        if random.choice([True, False]):
            return False, ""  # Pretend the operation was successful, do not show the modal
        else:
            # Operation failed, show the modal with a custom error message
            return True, "An unexpected error occurred!"

    elif button_id == "close-error-modal":
        return False, ""  # Close the modal and clear the error message
    return is_open, ""

if __name__ == "__main__":
    app.run_server(debug=True)