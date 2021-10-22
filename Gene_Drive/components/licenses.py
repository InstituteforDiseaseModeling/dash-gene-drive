import dash_bootstrap_components as dbc
from dash import html
import dash_renderjson
import json


with open("Gene_Drive/LICENSE.txt", "r") as f:
    our_license = f.readlines()

with open ("Gene_Drive/LICENSES.json", "r") as f:
    library_licenses_file = f.read()

library_licenses = json.loads(library_licenses_file)
library_licenses_content = []
for license in library_licenses:
    if license["Name"] == "Gene-Drive":
        license["License"] = "Creative Commons Attribution-ShareAlike"
    ul = html.Ul(
        children=[
            html.Li(
                children=[
                    html.Span(license["Name"]),
                    html.Ul(
                        [
                            html.Li(license["License"]),
                            html.Li(license["Version"])
                        ]
                    )
                ]
            )
        ]
    )
    library_licenses_content.append(ul)


tab1_content = html.P(
                className="mt-2 p-2",
                children= our_license
                )

tab2_content = html.Div(
                className="mt-2 p-1",
                children= library_licenses_content
                )

licenses_tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Our License", tab_id="our-license"),
        dbc.Tab(tab2_content, label="Library Licenses", tab_id="library-licenses"),
    ],
    active_tab="our-license"
)