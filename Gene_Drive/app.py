import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os
from components.about import about
from components.header import header
from components.footer import footer
from components.page_not_found import page_not_found


external_stylesheets = ['./assets/third_party_styles/bootstrap.min.css']
external_scripts = ['./assets/third_party_scripts/jquery-3.2.1.slim.min.js',
                    './assets/third_party_scripts/popper.min.js',
                    './assets/third_party_scripts/bootstrap.min.js']

# create an instant of a dash app
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                external_scripts=external_scripts,
                suppress_callback_exceptions=True)

server = app.server


# A function to wrap a component with header and footer
def layout(component=None):
    return html.Div(
        style={"height": "100%"},
        children=[
            header,
            component,
            footer
        ])


# define data_not_found page // different from 404
data_not_found = html.Div(
                          style={"height": "90vh"},
                          className="title",
                          children=[
                              html.H1("Error", className="display-1 text-center"),
                              html.H1("Data not found", className="display-1 text-center")
                          ])
# define the home_page
try:
    data_dir = os.getenv('DATA_DIR', None)
    if data_dir and os.path.exists(data_dir) and len(os.listdir(data_dir)) != 0:
        from components.gene_drive import GeneDriveAIO

        gene_drive_component = GeneDriveAIO()
    else:
        gene_drive_component = data_not_found
except:
    gene_drive_component = data_not_found

home_page = layout(gene_drive_component)

# define the about_page
about_page = layout(about)

# define the error page
error_page = layout(page_not_found)

# initiate the app layout
app.title = "Gene Drive"
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# add callbacks for page navigation
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home_page
    elif pathname == '/about':
        return about_page
    else:
        return error_page


if __name__ == '__main__':
    app.run_server(debug=False,
                   #TODO: switch port to 80
                   port=8050,
                   host='0.0.0.0')
