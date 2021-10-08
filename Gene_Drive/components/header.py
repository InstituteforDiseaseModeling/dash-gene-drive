import dash_bootstrap_components as dbc

header = dbc.NavbarSimple(
    fluid=True,
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("About", href="/about"))
    ],
    brand="Gene Drive",
    brand_href="/",
    color="#24323c",
    dark=True,
    sticky='top',
    className='p-0'
)
