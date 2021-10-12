import dash_bootstrap_components as dbc
from dash import html
import datetime

current_year = datetime.date.today().year

footer_style = {
    "position": "fixed",
    "bottom": 0,
    "width": "100%",
    "backgroundColor": "#24323c",
    "color": "white",
    "zIndex": 2000
}
logo_style = {
    "display": "inline-block",
    "margin": "15px 18px 10px 25px",
    "height": 35,
}

copy_text_style = {
    "fontSize": 14,
    "color": "#b1bcc5",
    "overflow": "hidden",
    "whiteSpace": "nowrap",
    "textOverflow": "ellipsis",
    "textAlign": "center",
    "marginTop": "15px"
}
terms_style = {
    "margin": "15px",
    "fontSize": 14,
    "textAlign": "right",
    "color": "#b8860b",
    "overflow": "hidden",
    "whiteSpace": "nowrap",
    "textOverflow": "ellipsis",
}
footer = html.Footer(style=footer_style, children=[
    dbc.Row(
        className="m-0 row d-none d-lg-flex",
        children=[
            dbc.Col(
                html.Img(style=logo_style, className="m-0 p-1", src='../assets/bmgf-logo-white.png')
            ),
            dbc.Col(
                [
                    html.Div(style=copy_text_style,
                             className="m-0",
                             children=[
                                 html.Span(f"1999-{current_year} Bill & Melinda Gates Foundation"),
                                 html.Br(),
                                 html.Span("All Rights Reserved")
                             ]
                             ),
                ]
            ),
            dbc.Col(
                html.Div(style=terms_style,
                         className="m-0",
                         children=[
                             html.A(style=terms_style,
                                    children=[
                                        html.Span(children=["Terms of Use"])
                                    ],
                                    href="https://www.gatesfoundation.org/Terms-of-Use"
                                    ),
                             html.Br(),
                             html.A(style=terms_style,
                                    children=[
                                        html.Span(children=["Privacy & Cookies Notice"])
                                    ],
                                    href="https://www.gatesfoundation.org/Privacy-and-Cookies-Notice"
                                    ),
                         ]
                         )
            ),
            dbc.Col(
                html.Img(style=logo_style, className="m-0", src='../assets/idmlogo55.png')
            )

        ]
    )
])
