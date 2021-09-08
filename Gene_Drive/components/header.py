import dash_bootstrap_components as dbc

header = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("About", href="/about"))
    ],
    brand="Gene_Drive",
    brand_href="/",
    color="#24323c",
    dark=True,
)
