import dash
import flask
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

class GeneDriveGreetingAIO(html.Div):
    def __init__(self):
        super().__init__([
            html.Div([
                dbc.Modal(
                    [

                        dbc.ModalBody(
                            children=[
                                dbc.Jumbotron(
                                    className="m-0 p-2",
                                    children=[
                                        html.H1("Gene Drive", className="display-3"),
                                        html.P(
                                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
                                            " Nam et augue nisi. Morbi finibus, tellus a congue accumsan,"
                                            " odio felis dictum orci, nec feugiat elit tellus tempus massa."
                                            " Quisque turpis est, sagittis nec euismod eget, dignissim et augue. "
                                            "Curabitur a mattis turpis. Aenean mattis ligula vel purus mollis "
                                            "rutrum. Nullam vitae nibh eu erat congue faucibus. Pellentesque "
                                            "pellentesque, ligula cursus rutrum rutrum, dolor tellus pharetra "
                                            "velit, id porta dui elit non mi. Fusce congue lacinia commodo. "
                                            "Nam pulvinar congue arcu, sed varius tellus tincidunt ac. "
                                            "Mauris lorem sapien, elementum eu lacinia sed, tempus sit "
                                            "amet elit. Nam laoreet molestie erat, eget commodo felis luctus ut.",
                                            className="lead",
                                        ),
                                        html.Hr(className="my-2"),
                                        html.P(
                                            "Click below to proceed to the website",
                                            className="text-center"
                                        ),
                                        html.P(
                                            dbc.Button(
                                                "Continue",
                                                id="close-greeting-modal",
                                                className="ml-auto",
                                                n_clicks=0,
                                                color="success",
                                                style={"minWidth": "300px"}
                                            ),
                                            className="text-center"

                                        ),
                                    ]
                                )
                            ]
                        ),
                    ],
                    id="greeting-modal",
                    is_open=True,
                    size='xl'
                ),
            ]
        )])


    @callback(
        Output("greeting-modal", "is_open"),
        [Input("close-greeting-modal", "n_clicks")],
    )
    def toggle_modal(n_clicks):
        if n_clicks != 0:
            dash.callback_context.response.set_cookie("greeting-modal-shown", "True")
            print("setting cookie 'greeting-modal-shown' True")
            return False
        all_cookies = dict(flask.request.cookies)
        if "greeting-modal-shown" in all_cookies and all_cookies["greeting-modal-shown"]== "True":
            return False
        return True