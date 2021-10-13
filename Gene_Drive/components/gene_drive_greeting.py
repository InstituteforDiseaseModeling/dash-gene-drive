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
                                        html.H3(
                                            children="Population replacement gene drives for "
                                                     "malaria elimination in a highly seasonal Sahelian setting"
                                        ),
                                        html.P(
                                            children="""
                                                    Using this website, you can explore the effects of a single release 
                                                    of gene drive mosquitoes with different values of various gene 
                                                    drive system and vector population parameters on malaria 
                                                    elimination probabilities and prevalence, as well as vector 
                                                    populations and genetics. Eight year-long simulations of 
                                                    population replacement gene drive mosquito release were run using 
                                                    EMOD 2.20 in a highly seasonal Sahelian setting over a 300 square 
                                                    kilometer region. Here elimination is defined as occurring when 
                                                    malaria prevalence reaches zero by the end of simulation year 7 
                                                    and remains at zero through the end of simulation year 8 across 
                                                    the entire spatial region.
                                                    """
                                        ),
                                        html.P(
                                            children=[
                                                html.Span(
                                                    children="The parameters that can be explored here include the following:"
                                                ),
                                                html.Ul(
                                                    children=[
                                                        html.Li(
                                                            children="The probability of copying over the driver and/or "
                                                                     "effector genes when the driver gene is present (also "
                                                                     "known as drive efficiency; d in the classic case, d1 "
                                                                     "in the integral case)"
                                                        ),
                                                        html.Li(
                                                            children="The ability of the introduced effector gene to suppress "
                                                                     "malaria transmission in mosquitoes (also known as the "
                                                                     "phenotypic effectiveness of the drive, rc)"
                                                        ),
                                                        html.Li(
                                                            children="The initial frequency of target site resistant alleles "
                                                                     "in the population (rr0 in the classic case, rr20 at the "
                                                                     "effector target site in the integral case)"
                                                        ),
                                                        html.Li(
                                                            children="The fitness cost associated with expressing the introduced "
                                                                     "driver and effector genes, represented by an increase in "
                                                                     "vector mortality (sne in the classic case, se2 associated "
                                                                     "with the effector in the integral case)."
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.P(
                                            children=[
                                                html.Span(
                                                    children="The paper associated with these visualizations and results can be found here: "
                                                ),
                                                html.A(
                                                    href="",
                                                    target="_blank",
                                                    children="<CITATION>. "
                                                ),
                                                html.Span(
                                                    children="Any questions can be sen to "
                                                ),
                                                html.A(
                                                    href="mailto:support@idmod.org",
                                                    children="support@idmod.org"
                                                ),
                                                html.Span(".")

                                            ]
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
        if "greeting-modal-shown" in all_cookies and all_cookies["greeting-modal-shown"] == "True":
            return False
        return True
