import dash_html_components as html

about = html.Div(
    style={"height":"90vh"},
    className="content", children=[
    html.H4(className="title titleText", children="What is Gene Drive?"),
    html.P(children="Gene Drive is ..."),
])
