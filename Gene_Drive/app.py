import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from components.about import about
from components.header import header
from components.footer import footer
from components.page_not_found import page_not_found
from components.gene_drive import GeneDriveAIO


external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://code.jquery.com/jquery-3.2.1.slim.min.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
                    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js']

# create an instant of a dash app
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                external_scripts=external_scripts,
                suppress_callback_exceptions=True)

# A function to wrap a component with header and footer
def layout(component=None):
    return html.Div(children=[
        header,
        component,
        footer
    ])


# define the home_page
# replace sample_chart with your own chart or component
gene_drive_component = GeneDriveAIO()
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
    app.run_server(debug=False, host='0.0.0.0')
