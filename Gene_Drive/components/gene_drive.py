import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, clientside_callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import plotly.colors as colors
from .gene_drive_greeting import GeneDriveGreetingAIO
from Gene_Drive.app import cache


#--------- Define colorscale for matrices
greens_r_full = colors.get_colorscale('greens_r')
greens_r = greens_r_full[:-1]
for i in range(0, len(greens_r)):
    greens_r[i][0] = i/(len(greens_r)-1)

# -------- Choose experiment and set up params
svs_by_drive_type = {
    'Classic': {'rc': 'rc (tansm.-blocking eff.)',
                'd': 'd (drive efficiency)',
                'rr0': 'rr0 (pre-ex. resistance)',
                'sne': 'sne (fitness cost)'},
    'Integral': {'rc': 'rc (tansm.-blocking eff.)',
                 'd1': 'd1 (drive efficiency)',
                 'rr20': 'rr20 (pre-ex. resistance)',
                 'se2': 'se2 (fitness cost)'}
}

sv_vals_by_drive_type = {
    'Classic': {
        'rc': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        'd': [0.9, 0.95, 1.0],
        'rr0': [0.0, 0.001, 0.01, 0.1],
        'sne': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    },
    'Integral': {
        'rc': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        'd1': [0.9, 0.95, 1.0],
        'rr20': [0.0, 0.001, 0.01, 0.1],
        'se2': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    }
}

sv_defs_by_drive_type = {
    'Classic': {
        'rc': 1.0, 'd': 1.0, 'sne': 0.0, 'rr0': 0.0
    },
    'Integral': {
        'rc': 1.0, 'd1': 1.0, 'se2': 0.0, 'rr20': 0.0
    }
}

alleles_by_drive_type = {
    'Classic': {
        'wt_allele': 'a0',
        'effector_allele': 'a1',
        'resistance_allele': 'a2'
    },
    'Integral': {
        'wt_allele': 'b0',
        'effector_allele': 'b1',
        'resistance_allele': 'b2'
    }
}

eirs_itns = [
    'EIR = 10, no ITNs',
    'EIR = 10, with ITNs',
    'EIR = 30, no ITNs',
    'EIR = 30, with ITNs',
    'EIR = 80, with ITNs',
]

fns_by_drive_type_eir_itn = {
    'Classic': {
        'EIR = 10, no ITNs': 'spatialinside_classic3allele_GM_only_aEIR10_sweep_rc_d_rr0_sne',
        'EIR = 10, with ITNs': 'spatialinside_classic3allele_VC_and_GM_aEIR10_sweep_rc_d_rr0_sne',
        'EIR = 30, no ITNs': 'spatialinside_classic3allele_GM_only_aEIR30_sweep_rc_d_rr0_sne',
        'EIR = 30, with ITNs': 'spatialinside_classic3allele_VC_and_GM_aEIR30_sweep_rc_d_rr0_sne',
        'EIR = 80, with ITNs': 'spatialinside_classic3allele_VC_and_GM_aEIR80_sweep_rc_d_rr0_sne'
    },
    'Integral': {
        'EIR = 10, no ITNs': 'spatialinside_integral2l4a_GM_only_aEIR10_sweep_rc_d1_rr20_se2',
        'EIR = 10, with ITNs': 'spatialinside_integral2l4a_VC_and_GM_aEIR10_sweep_rc_d1_rr20_se2',
        'EIR = 30, no ITNs': 'spatialinside_integral2l4a_GM_only_aEIR30_sweep_rc_d1_rr20_se2',
        'EIR = 30, with ITNs': 'spatialinside_integral2l4a_VC_and_GM_aEIR30_sweep_rc_d1_rr20_se2',
        'EIR = 80, with ITNs': 'spatialinside_integral2l4a_VC_and_GM_aEIR80_sweep_rc_d1_rr20_se2'
    }
}

itn_distrib_days = [180, 3 * 365 + 180, 6 * 365 + 180]
released_day = 180
num_yrs = 8  # length of sim
num_seeds = 20  # num of seeds per sim
elim_day = 2555  # day on which elim fraction is calculated

data_dir = os.getenv('DATA_DIR', None)

##
# -------- Load data
dfis = {}
dfas = {}
dfes = {}
dfeds = {}
print("starting data load")
last_winame = None
for drive_typenow in fns_by_drive_type_eir_itn.keys():
    for eir_itnnow in fns_by_drive_type_eir_itn[drive_typenow].keys():
        winame = fns_by_drive_type_eir_itn[drive_typenow][eir_itnnow]
        print("loading data...")
        dfis[winame] = pd.read_feather(os.path.join(data_dir, 'dfi_' + winame + '.feather'))
        dfas[winame] = pd.read_feather(os.path.join(data_dir, 'dfa_' + winame + '.feather'))
        dfes[winame] = pd.read_feather(os.path.join(data_dir, 'dfe_' + winame + '.feather'))
        dfeds[winame] = pd.read_feather(os.path.join(data_dir, 'dfed_' + winame + '.feather'))
        last_winame = winame
    for column in sv_vals_by_drive_type[drive_typenow].keys():
        sv_vals_by_drive_type[drive_typenow][column] = np.asarray(sv_vals_by_drive_type[drive_typenow][column],
                                                                  dtype=dfes[last_winame].dtypes[column])
print("data load complete")
##
# -------- Component
class GeneDriveAIO(html.Div):
    def __init__(self):
        super().__init__([
            html.Div([
                GeneDriveGreetingAIO(),
                dcc.Tabs([

                    dcc.Tab(
                        className="p-1",
                        label='Elimination probability matrices',
                        children=[

                            html.H3(className="m-2 text-center", children='Elimination probabilities'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(
                                                                bs_size="sm",
                                                                id='eir-itn0',
                                                                options=[{'label': i, 'value': i} for i in
                                                                         list(eirs_itns)],
                                                                value='EIR = 30, with ITNs'
                                                            )
                                                        ],
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type0',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ],
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar0')
                                                        ],
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar0')
                                                        ],
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Matrix x-var:']),
                                                            dbc.Select(bs_size="sm", id='matrix-xvar0')
                                                        ],
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Matrix y-var:']),
                                                            dbc.Select(bs_size="sm", id='matrix-yvar0')
                                                        ],
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-elim-prob-matrices",
                                            style={"height": "100%"},
                                        )
                                    ),
                                    html.Div(
                                        className="col-12 mt-1 pr-0",
                                        children=[
                                            dbc.Alert(
                                                id="elim-prob-matrices-err-msg",
                                                children="Outer x-var, Outer y-var, Matrix x-var ,and Matrix y-var "
                                                         "values must all be different",
                                                color="danger",
                                                dismissable=False,
                                                className="removed mb-0 p-1"
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            html.H2(
                                id="display-elim-prob-matrices",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='elim-prob-matrices',
                                          className="removed",
                                          style={'width': '100%', 'height': 'calc(100vh - 318px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1", label='Years to elimination matrices', children=[

                            html.H3(className="m-2 text-center", children='Years to elimination'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn1',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ],
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type1',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ],
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar1')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar1')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Matrix x-var:']),
                                                            dbc.Select(bs_size="sm", id='matrix-xvar1')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Matrix y-var:']),
                                                            dbc.Select(bs_size="sm", id='matrix-yvar1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-elim-time-matrices",

                                            style={"height": "100%"}
                                        )
                                    ),
                                    html.Div(
                                        className="col-12 mt-1 pr-0",
                                        children=[
                                            dbc.Alert(
                                                id="elim-time-matrices-err-msg",
                                                children="Outer x-var, Outer y-var, Matrix x-var ,and Matrix y-var "
                                                         "values must all be different",
                                                color="danger",
                                                dismissable=False,
                                                className="removed mb-0 p-1"
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            html.H2(
                                id="display-elim-time-matrices",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='elim-time-matrices',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 318px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        label='Prevalence time series',
                        id="prev-ts-tab",
                        children=[

                            html.H3(className="m-2 text-center", children='Prevalence'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn2',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type2',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar2')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar2')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var2-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var2-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-prev-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-prev-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='prev-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="av-ts-tab",
                        label='Adult vectors time series',
                        children=[

                            html.H3(className="m-2 text-center", children='Adult vectors'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn3',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type3',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar3')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar3')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var3-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var3-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        id="run-av-ts",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-av-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='av-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="ivf-ts-tab",
                        label='Infectious fraction time series',
                        children=[

                            html.H3(className="m-2 text-center", children='Infectious vector fraction'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn4',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type4',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar4')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar4')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var4-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var4-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-ivf-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-ivf-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='ivf-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="ivn-ts-tab",
                        label='Infectious vectors time series',
                        children=[

                            html.H3(className="m-2 text-center", children='Infectious vectors'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn5',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type5',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar5')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar5')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var5-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var5-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-ivn-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-ivn-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='ivn-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="ef-ts-tab",
                        label='Effector frequency time series',
                        children=[

                            html.H3(className="m-2 text-center",
                                    children='Effector frequency (or drive+effector in classic drive case)'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn6',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type6',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )

                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar6')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar6')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var6-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var6-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-ef-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-ef-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='ef-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="wt-ts-tab",
                        label='Wild type frequency time series',
                        children=[

                            html.H3(className="m-2 text-center",
                                    children='Wild type frequency (at effector locus in integral drive case)'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn7',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type7',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar7')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar7')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var7-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var7-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-wt-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-wt-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='wt-ts',
                                          className='removed',
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ]),

                    dcc.Tab(
                        className="p-1",
                        id="rs-ts-tab",
                        label='Resistance frequency time series',
                        children=[

                            html.H3(className="m-2 text-center",
                                    children='Resistance frequency (at effector locus in integral drive case)'),
                            html.Div(
                                className="container-fluid row m-0",
                                children=[
                                    # drop downs
                                    html.Div(
                                        className="col-11",
                                        children=[
                                            # first row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['EIR and ITNs:']),
                                                            dbc.Select(bs_size="sm",
                                                                       id='eir-itn8',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(eirs_itns)],
                                                                       value='EIR = 30, with ITNs'
                                                                       )
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Drive type:'], ),
                                                            dbc.Select(bs_size="sm",
                                                                       id='drive-type8',
                                                                       options=[{'label': i, 'value': i} for i in
                                                                                list(svs_by_drive_type.keys())],
                                                                       value='Integral'
                                                                       )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            # second row of drop downs
                                            html.Div(
                                                className="row",
                                                children=[
                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer x-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-xvar8')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['Outer y-var:']),
                                                            dbc.Select(bs_size="sm", id='outer-yvar8')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['1st plot var (color):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var8-0')
                                                        ]
                                                    ),

                                                    html.Div(
                                                        className="col-3",
                                                        children=[
                                                            html.Label(className="m-0 font-weight-bold",
                                                                       children=['2nd plot var (style):']),
                                                            dbc.Select(bs_size="sm", id='sweep-var8-1')
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    # run button
                                    html.Div(
                                        className="col-1 border-left pr-0",
                                        children=html.Button(
                                            className="btn btn-lg btn-primary btn-block",
                                            children="Run",
                                            id="run-rs-ts",

                                            style={"height": "100%"}
                                        )
                                    )
                                ]
                            ),
                            html.H2(
                                id="display-rs-ts",
                                className="text-center text-secondary shown mt-5 pt-5",
                                children="Click 'Run' to display graphs/matrices."
                            ),
                            html.Div([
                                dcc.Graph(id='rs-ts',
                                          className="removed",
                                          style={'width': '100%', 'height': 'calc(100vh - 313px)'})
                            ])
                        ])

                ])
            ])
        ])

    # ---------------------------------------------
    # Callbacks for updating tab labels so that
    # "time series" is in its own line
    # ---------------------------------------------
    tab_label_updater = """
    function(tab_id) {
        let label = document.evaluate(`//*[@id="${tab_id}"]/span`, document, null, XPathResult.ANY_TYPE, null);
        if(label) {   
            try {
                label_to_edit = label.iterateNext()
                label_to_edit.innerHTML = label_to_edit.textContent.replace("time series", "<br>time series");
            }catch(err){
                console.log(err)
            }
        }
    } 
    """
    time_series_tab_ids = ["prev-ts-tab", "av-ts-tab", "ivf-ts-tab",
                           "ivn-ts-tab", "ef-ts-tab", "wt-ts-tab", "rs-ts-tab"]
    for tab_id in time_series_tab_ids:
        clientside_callback(
            tab_label_updater,
            Output(tab_id, 'value'),
            Input(tab_id, 'id')
        )

    # ---------------------------------------------
    # Callbacks for dropdowns to update dropdowns
    # ---------------------------------------------

    # ---- Elim prob matrices
    @callback(
        [Output('outer-xvar0', 'options'),
         Output('outer-yvar0', 'options'),
         Output('matrix-xvar0', 'options'),
         Output('matrix-yvar0', 'options')],
        [Input('drive-type0', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar0', 'value'),
         Output('outer-yvar0', 'value'),
         Output('matrix-xvar0', 'value'),
         Output('matrix-yvar0', 'value'),
         Output('elim-prob-matrices-err-msg', 'className'),
         Output('run-elim-prob-matrices', 'disabled')],
        [Input('outer-xvar0', 'options'),
         Input('outer-yvar0', 'options'),
         Input('matrix-xvar0', 'options'),
         Input('matrix-yvar0', 'options'),
         Input('outer-xvar0', 'value'),
         Input('outer-yvar0', 'value'),
         Input('matrix-xvar0', 'value'),
         Input('matrix-yvar0', 'value')
         ])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts,
                     outer_xvar, outer_yvar, matrix_xvar, matrix_yvar):
        error_response = dash.no_update, dash.no_update, dash.no_update, dash.no_update, "shown mb-0 p-1", True
        success_response = outer_xvar, outer_yvar, matrix_xvar, matrix_yvar, "removed mb-0 p-1", False

        ctx = dash.callback_context
        if len(ctx.triggered) == 1:
            if len(set([outer_xvar, outer_yvar, matrix_xvar, matrix_yvar])) != 4:
                return error_response
            else:
                return success_response
        else:
            return outer_xvar_opts[0]['value'], outer_yvar_opts[1]['value'], \
                   matrix_xvar_opts[2]['value'], matrix_yvar_opts[3]['value'], "removed mb-0 p-1", False

    # ---- Elim time matrices
    @callback(
        [Output('outer-xvar1', 'options'),
         Output('outer-yvar1', 'options'),
         Output('matrix-xvar1', 'options'),
         Output('matrix-yvar1', 'options')],
        [Input('drive-type1', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar1', 'value'),
         Output('outer-yvar1', 'value'),
         Output('matrix-xvar1', 'value'),
         Output('matrix-yvar1', 'value'),
         Output('elim-time-matrices-err-msg', 'className'),
         Output('run-elim-time-matrices', 'disabled')],
        [Input('outer-xvar1', 'options'),
         Input('outer-yvar1', 'options'),
         Input('matrix-xvar1', 'options'),
         Input('matrix-yvar1', 'options'),
         Input('outer-xvar1', 'value'),
         Input('outer-yvar1', 'value'),
         Input('matrix-xvar1', 'value'),
         Input('matrix-yvar1', 'value')
         ])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts,
                     outer_xvar, outer_yvar, matrix_xvar, matrix_yvar):
        error_response = dash.no_update, dash.no_update, dash.no_update, dash.no_update, "shown", True
        success_response = outer_xvar, outer_yvar, matrix_xvar, matrix_yvar, "removed", False

        ctx = dash.callback_context
        if len(ctx.triggered) == 1:
            if len(set([outer_xvar, outer_yvar, matrix_xvar, matrix_yvar])) != 4:
                return error_response
            else:
                return success_response
        else:
            return outer_xvar_opts[0]['value'], outer_yvar_opts[1]['value'], \
                   matrix_xvar_opts[2]['value'], matrix_yvar_opts[3]['value'], "removed", False

    # ---- Prev ts
    @callback(
        [Output('outer-xvar2', 'options'),
         Output('outer-yvar2', 'options'),
         Output('sweep-var2-0', 'options'),
         Output('sweep-var2-1', 'options')],
        [Input('drive-type2', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar2', 'value'),
         Output('outer-yvar2', 'value'),
         Output('sweep-var2-0', 'value'),
         Output('sweep-var2-1', 'value')],
        [Input('outer-xvar2', 'options'),
         Input('outer-yvar2', 'options'),
         Input('sweep-var2-0', 'options'),
         Input('sweep-var2-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Adult vector ts
    @callback(
        [Output('outer-xvar3', 'options'),
         Output('outer-yvar3', 'options'),
         Output('sweep-var3-0', 'options'),
         Output('sweep-var3-1', 'options')],
        [Input('drive-type3', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar3', 'value'),
         Output('outer-yvar3', 'value'),
         Output('sweep-var3-0', 'value'),
         Output('sweep-var3-1', 'value')],
        [Input('outer-xvar3', 'options'),
         Input('outer-yvar3', 'options'),
         Input('sweep-var3-0', 'options'),
         Input('sweep-var3-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Infectious vector fraction ts
    @callback(
        [Output('outer-xvar4', 'options'),
         Output('outer-yvar4', 'options'),
         Output('sweep-var4-0', 'options'),
         Output('sweep-var4-1', 'options')],
        [Input('drive-type4', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar4', 'value'),
         Output('outer-yvar4', 'value'),
         Output('sweep-var4-0', 'value'),
         Output('sweep-var4-1', 'value')],
        [Input('outer-xvar4', 'options'),
         Input('outer-yvar4', 'options'),
         Input('sweep-var4-0', 'options'),
         Input('sweep-var4-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Infectious vectors ts
    @callback(
        [Output('outer-xvar5', 'options'),
         Output('outer-yvar5', 'options'),
         Output('sweep-var5-0', 'options'),
         Output('sweep-var5-1', 'options')],
        [Input('drive-type5', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar5', 'value'),
         Output('outer-yvar5', 'value'),
         Output('sweep-var5-0', 'value'),
         Output('sweep-var5-1', 'value')],
        [Input('outer-xvar5', 'options'),
         Input('outer-yvar5', 'options'),
         Input('sweep-var5-0', 'options'),
         Input('sweep-var5-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Effector freq ts
    @callback(
        [Output('outer-xvar6', 'options'),
         Output('outer-yvar6', 'options'),
         Output('sweep-var6-0', 'options'),
         Output('sweep-var6-1', 'options')],
        [Input('drive-type6', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar6', 'value'),
         Output('outer-yvar6', 'value'),
         Output('sweep-var6-0', 'value'),
         Output('sweep-var6-1', 'value')],
        [Input('outer-xvar6', 'options'),
         Input('outer-yvar6', 'options'),
         Input('sweep-var6-0', 'options'),
         Input('sweep-var6-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Wild type freq ts
    @callback(
        [Output('outer-xvar7', 'options'),
         Output('outer-yvar7', 'options'),
         Output('sweep-var7-0', 'options'),
         Output('sweep-var7-1', 'options')],
        [Input('drive-type7', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar7', 'value'),
         Output('outer-yvar7', 'value'),
         Output('sweep-var7-0', 'value'),
         Output('sweep-var7-1', 'value')],
        [Input('outer-xvar7', 'options'),
         Input('outer-yvar7', 'options'),
         Input('sweep-var7-0', 'options'),
         Input('sweep-var7-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---- Resistance freq ts
    @callback(
        [Output('outer-xvar8', 'options'),
         Output('outer-yvar8', 'options'),
         Output('sweep-var8-0', 'options'),
         Output('sweep-var8-1', 'options')],
        [Input('drive-type8', 'value')])
    def set_sv_options(sel_drive_type):
        outer_xvar_opts = svs_by_drive_type[sel_drive_type]
        outer_yvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_xvar_opts = svs_by_drive_type[sel_drive_type]
        matrix_yvar_opts = svs_by_drive_type[sel_drive_type]
        return [{'label': outer_xvar_opts[i], 'value': i} for i in outer_xvar_opts], \
               [{'label': outer_yvar_opts[i], 'value': i} for i in outer_yvar_opts], \
               [{'label': matrix_xvar_opts[i], 'value': i} for i in matrix_xvar_opts], \
               [{'label': matrix_yvar_opts[i], 'value': i} for i in matrix_yvar_opts]

    @callback(
        [Output('outer-xvar8', 'value'),
         Output('outer-yvar8', 'value'),
         Output('sweep-var8-0', 'value'),
         Output('sweep-var8-1', 'value')],
        [Input('outer-xvar8', 'options'),
         Input('outer-yvar8', 'options'),
         Input('sweep-var8-0', 'options'),
         Input('sweep-var8-1', 'options')])
    def set_sv_value(outer_xvar_opts, outer_yvar_opts, matrix_xvar_opts, matrix_yvar_opts):
        return outer_xvar_opts[0]['value'], outer_yvar_opts[2]['value'], \
               matrix_xvar_opts[3]['value'], matrix_yvar_opts[1]['value']

    # ---------------------------------------------
    # Callbacks for figures
    # ---------------------------------------------
    # ---- Elim prob matrices
    @callback(
        [Output('elim-prob-matrices', 'figure'),
         Output('elim-prob-matrices', 'className'),
         Output('display-elim-prob-matrices', 'className'),
         Output('run-elim-prob-matrices', 'n_clicks')],
        [Input('run-elim-prob-matrices', 'n_clicks'),
         State('eir-itn0', 'value'),
         State('drive-type0', 'value'),
         State('outer-xvar0', 'value'),
         State('outer-yvar0', 'value'),
         State('matrix-xvar0', 'value'),
         State('matrix-yvar0', 'value'), ]
    )
    @cache.memoize()
    def update_elim_prob_matrices(n_clicks, sel_eir_itn, sel_drive_type,
                                  ov_xvar, ov_yvar, mat_xvar, mat_yvar):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfe = dfes[winame]

        # - Get all outer xvar and yvar vals
        ov_xvar_vals = svvals[ov_xvar]
        ov_yvar_vals = svvals[ov_yvar]

        # - Compute subplot titles and heatmaps
        iaxis = 1
        subplots = []

        dfe = dfe[dfe[mat_xvar].isin(svvals[mat_xvar]) &
                      dfe[mat_yvar].isin(svvals[mat_yvar])]

        for ov_yvar_val in ov_yvar_vals:
            for ov_xvar_val in ov_xvar_vals:

                # - Compute heatmap values
                allvardefsnow = {k: v for k, v in svdefs.items() if k not in [mat_xvar, mat_yvar, ov_xvar, ov_yvar]}
                dfenow = dfe
                if len(allvardefsnow) > 0:
                    for k, v in allvardefsnow.items():
                        dfenow = dfenow[dfenow[k] == v]
                        dfenow.drop(columns=[k], inplace=True)
                dfenow = dfenow[dfenow[ov_xvar] == ov_xvar_val]
                dfenow = dfenow[dfenow[ov_yvar] == ov_yvar_val]
                dfenow.drop(columns=[ov_xvar, ov_yvar], inplace=True)
                dfenow = (dfenow.groupby([mat_xvar, mat_yvar])[
                                 'True_Prevalence_elim'].sum() / num_seeds).reset_index()
                matnow = dfenow.pivot_table(index=[mat_yvar], columns=[mat_xvar], values='True_Prevalence_elim')

                # - Create annotated heatmap
                subplots.append(ff.create_annotated_heatmap(
                    z=matnow.values,
                    x=list(range(len(svvals[mat_xvar]))),
                    y=list(range(len(svvals[mat_yvar]))),
                    zmin=0,
                    zmax=1,
                    showscale=True,
                    colorscale=greens_r)
                )

                # - Update annotation axes
                for annot in subplots[-1]['layout']['annotations']:
                    annot['xref'] = 'x' + str(iaxis)
                    annot['yref'] = 'y' + str(iaxis)
                iaxis = iaxis + 1

        # - Set up subplot framework and titles
        fig = make_subplots(
            rows=len(ov_yvar_vals), cols=len(ov_xvar_vals),
            shared_xaxes=True,
            shared_yaxes=True,
            column_titles=[ov_xvar + '=' + str(val) for val in ov_xvar_vals],
            row_titles=[ov_yvar + '=' + str(val) for val in ov_yvar_vals],
            x_title=mat_xvar,
            y_title=mat_yvar,
            horizontal_spacing=0.03,
            vertical_spacing=0.03
        )

        # - Create each subplot
        isp = 0
        for irow, ov_yvar_val in enumerate(ov_yvar_vals):
            for icol, ov_xvar_val in enumerate(ov_xvar_vals):
                fig.add_trace(subplots[isp].data[0], row=irow + 1, col=icol + 1)
                isp = isp + 1

        # - Update annotations for all subplot
        for isp, subplot in enumerate(subplots):
            fig.layout.annotations += subplots[isp].layout.annotations

        # - Update fig layout and subplot axes
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(len(svvals[mat_xvar]))),
            ticktext=[str(val) for val in svvals[mat_xvar]]
        )
        fig.update_yaxes(
            tickmode='array',
            tickvals=list(range(len(svvals[mat_yvar]))),
            ticktext=[str(val) for val in svvals[mat_yvar]]
        )
        fig.update_layout(margin=dict(l=60, r=50, b=50, t=30))

        return fig, 'shown', 'removed' , None

    # ---- Elim time matrices
    @callback(
        Output('elim-time-matrices', 'figure'),
        Output('elim-time-matrices', 'className'),
        Output('display-elim-time-matrices', 'className'),
        Output('run-elim-time-matrices', 'n_clicks'),
        [State('eir-itn1', 'value'),
         State('drive-type1', 'value'),
         State('outer-xvar1', 'value'),
         State('outer-yvar1', 'value'),
         State('matrix-xvar1', 'value'),
         State('matrix-yvar1', 'value'),
         Input('run-elim-time-matrices', 'n_clicks')])
    @cache.memoize()
    def update_elim_time_matrices(sel_eir_itn, sel_drive_type,
                                  ov_xvar, ov_yvar, mat_xvar, mat_yvar, n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfed = dfeds[winame]

        # - Get all outer xvar and yvar vals
        ov_xvar_vals = svvals[ov_xvar]
        ov_yvar_vals = svvals[ov_yvar]

        # - Compute subplot titles and heatmaps
        iaxis = 1
        subplots = []

        dfed = dfed[dfed[mat_xvar].isin(svvals[mat_xvar]) &
                      dfed[mat_yvar].isin(svvals[mat_yvar])]

        for ov_yvar_val in ov_yvar_vals:
            for ov_xvar_val in ov_xvar_vals:

                # - Compute heatmap values
                svdefsnow = {k: v for k, v in svdefs.items() if k not in [mat_xvar, mat_yvar, ov_xvar, ov_yvar]}
                dfednow = dfed
                if len(svdefsnow) > 0:
                    for k, v in svdefsnow.items():
                        dfednow = dfednow[dfednow[k] == v]
                        dfednow.drop(columns=[k], inplace=True)
                dfednow = dfednow[dfednow[ov_xvar] == ov_xvar_val]
                dfednow = dfednow[dfednow[ov_yvar] == ov_yvar_val]
                dfednow.drop(columns=[ov_xvar, ov_yvar], inplace=True)
                dfednow.loc[dfednow['True_Prevalence_elim'] == False,
                            'True_Prevalence_elim_day'] = np.nan
                dfednow.drop(columns=['True_Prevalence_elim'], inplace=True)
                dfednow = (dfednow.groupby([mat_xvar, mat_yvar])['True_Prevalence_elim_day'].mean()).reset_index()
                matnow = dfednow.pivot_table(index=[mat_yvar], columns=[mat_xvar],
                                                values='True_Prevalence_elim_day', dropna=False)
                matnow = (matnow / 365).round(1)  # .astype('Int64')

                # - Create annotated heatmap
                subplots.append(ff.create_annotated_heatmap(
                    z=matnow.values,
                    x=list(range(len(svvals[mat_xvar]))),
                    y=list(range(len(svvals[mat_yvar]))),
                    # zmin=(dfed['True_Prevalence_elim_day'] / 365).min(),
                    # zmax=(dfed['True_Prevalence_elim_day'] / 365).max(),
                    zmin=2.5,
                    zmax=num_yrs,
                    showscale=True,
                    colorscale=greens_r)
                )

                # - Update annotation axes
                for annot in subplots[-1]['layout']['annotations']:
                    annot['xref'] = 'x' + str(iaxis)
                    annot['yref'] = 'y' + str(iaxis)
                iaxis = iaxis + 1

        # - Set up subplot framework
        fig = make_subplots(
            rows=len(ov_yvar_vals), cols=len(ov_xvar_vals),
            shared_xaxes=True,
            shared_yaxes=True,
            column_titles=[ov_xvar + '=' + str(val) for val in ov_xvar_vals],
            row_titles=[ov_yvar + '=' + str(val) for val in ov_yvar_vals],
            x_title=mat_xvar,
            y_title=mat_yvar,
            horizontal_spacing=0.03,
            vertical_spacing=0.03
        )

        # - Create each subplot
        isp = 0
        for irow, ov_yvar_val in enumerate(ov_yvar_vals):
            for icol, ov_xvar_val in enumerate(ov_xvar_vals):
                fig.add_trace(subplots[isp].data[0], row=irow + 1, col=icol + 1)
                isp = isp + 1

        # - Update annotations for all subplots
        for isp, subplot in enumerate(subplots):
            fig.layout.annotations += subplots[isp].layout.annotations

        # - Update fig layout and subplot axes
        fig.update_xaxes(
            ticklen=10,
            tickmode='array',
            tickvals=list(range(len(svvals[mat_xvar]))),
            ticktext=[str(val) for val in svvals[mat_xvar]]
        )
        fig.update_yaxes(
            ticklen=10,
            tickmode='array',
            tickvals=list(range(len(svvals[mat_yvar]))),
            ticktext=[str(val) for val in svvals[mat_yvar]]
        )
        fig.update_layout(margin=dict(l=60, r=50, b=50, t=30))

        return fig, 'shown', 'removed', None

    # ---- Prevalence time series
    @callback(
        Output('prev-ts', 'figure'),
        Output('prev-ts', 'className'),
        Output('display-prev-ts', 'className'),
        Output('run-prev-ts', 'n_clicks'),
        [Input('run-prev-ts', 'n_clicks'),
         State('eir-itn2', 'value'),
         State('drive-type2', 'value'),
         State('outer-xvar2', 'value'),
         State('outer-yvar2', 'value'),
         State('sweep-var2-0', 'value'),
         State('sweep-var2-1', 'value'),
         ])
    @cache.memoize()
    def update_prev_ts(n_clicks, sel_eir_itn, sel_drive_type,
                       ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfi = dfis[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfi = dfi[dfi[k] == v]
            dfi = dfi.drop(columns=[k], inplace=True)
        dfi = dfi[[svar0, svar1, ov_xvar, ov_yvar, 'Time', 'True Prevalence']]
        dfi = dfi[dfi[svar0].isin(svvals[svar0]) &
                  dfi[svar1].isin(svvals[svar1]) &
                  dfi[ov_xvar].isin(svvals[ov_xvar]) &
                  dfi[ov_yvar].isin(svvals[ov_yvar])]

        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfi[var] = dfi[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfi, x='Time', y='True Prevalence',
                      labels={
                          'True Prevalence': '',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-0.06, 1.06])
        return fig, 'shown', 'removed', None

    # ---- Adult vector time series
    @callback(
        Output('av-ts', 'figure'),
        Output('av-ts', 'className'),
        Output('display-av-ts', 'className'),
        Output('run-av-ts', 'n_clicks'),
        [Input('run-av-ts', 'n_clicks'),
         State('eir-itn3', 'value'),
         State('drive-type3', 'value'),
         State('outer-xvar3', 'value'),
         State('outer-yvar3', 'value'),
         State('sweep-var3-0', 'value'),
         State('sweep-var3-1', 'value'),
         ])
    @cache.memoize()
    def update_av_ts(n_clicks, sel_eir_itn, sel_drive_type,
                     ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfi = dfis[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfi = dfi[dfi[k] == v]
            dfi = dfi.drop(columns=[k], inplace=True)
        dfi = dfi[[svar0, svar1, ov_xvar, ov_yvar, 'Time', 'Adult Vectors']]
        dfi = dfi[dfi[svar0].isin(svvals[svar0]) &
                  dfi[svar1].isin(svvals[svar1]) &
                  dfi[ov_xvar].isin(svvals[ov_xvar]) &
                  dfi[ov_yvar].isin(svvals[ov_yvar])]

        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfi[var] = dfi[var].astype(float).round(3)

        # - Plot
        fig = px.line(dfi, x='Time', y='Adult Vectors',
                      labels={
                          'Adult Vectors': '#',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-50, 8500])
        return fig, 'shown', 'removed', None

    # ---- Infectious vector fraction time series
    @callback(
        Output('ivf-ts', 'figure'),
        Output('ivf-ts', 'className'),
        Output('display-ivf-ts', 'className'),
        Output('run-ivf-ts', 'n_clics'),
        [Input('run-ivf-ts', 'n_clicks'),
         State('eir-itn4', 'value'),
         State('drive-type4', 'value'),
         State('outer-xvar4', 'value'),
         State('outer-yvar4', 'value'),
         State('sweep-var4-0', 'value'),
         State('sweep-var4-1', 'value'),
         ])
    @cache.memoize()
    def update_ivf_ts(n_clicks, sel_eir_itn, sel_drive_type,
                      ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfi = dfis[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfi = dfi[dfi[k] == v]
            dfi = dfi.drop(columns=[k], inplace=True)
        dfi = dfi[[svar0, svar1, ov_xvar, ov_yvar, 'Time', 'Infectious Vectors']]
        dfi = dfi[dfi[svar0].isin(svvals[svar0]) &
                  dfi[svar1].isin(svvals[svar1]) &
                  dfi[ov_xvar].isin(svvals[ov_xvar]) &
                  dfi[ov_yvar].isin(svvals[ov_yvar])]

        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfi[var] = dfi[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfi, x='Time', y='Infectious Vectors',
                      labels={
                          'Infectious Vectors': '',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-0.01, 0.12])
        return fig, 'shown', 'removed', None

    # ---- Infectious vector numbers time series
    @callback(
        Output('ivn-ts', 'figure'),
        Output('ivn-ts', 'className'),
        Output('display-ivn-ts', 'className'),
        Output('run-ivn-ts', 'n_clicks'),
        [Input('run-ivn-ts', 'n_clicks'),
         State('eir-itn5', 'value'),
         State('drive-type5', 'value'),
         State('outer-xvar5', 'value'),
         State('outer-yvar5', 'value'),
         State('sweep-var5-0', 'value'),
         State('sweep-var5-1', 'value'),
         ])
    @cache.memoize()
    def update_ivn_ts(n_clicks, sel_eir_itn, sel_drive_type,
                      ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        dfi = dfis[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfi = dfi[dfi[k] == v]
            dfi = dfi.drop(columns=[k], inplace=True)
        dfi = dfi[[svar0, svar1, ov_xvar, ov_yvar, 'Time', 'Infectious Vectors Num']]
        dfi = dfi[dfi[svar0].isin(svvals[svar0]) &
                  dfi[svar1].isin(svvals[svar1]) &
                  dfi[ov_xvar].isin(svvals[ov_xvar]) &
                  dfi[ov_yvar].isin(svvals[ov_yvar])]

        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfi[var] = dfi[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfi, x='Time', y='Infectious Vectors Num',
                      labels={
                          'Infectious Vectors Num': '#',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-5, 165])
        return fig, 'shown', 'removed', None

    # ---- Effector freq time series
    @callback(
        Output('ef-ts', 'figure'),
        Output('ef-ts', 'className'),
        Output('display-ef-ts', 'className'),
        Output('run-ef-ts', 'n_clicks'),
        [Input('run-ef-ts', 'n_clicks'),
         State('eir-itn6', 'value'),
         State('drive-type6', 'value'),
         State('outer-xvar6', 'value'),
         State('outer-yvar6', 'value'),
         State('sweep-var6-0', 'value'),
         State('sweep-var6-1', 'value'),
         ])
    @cache.memoize()
    def update_ef_ts(n_clicks, sel_eir_itn, sel_drive_type,
                     ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        effallele = alleles_by_drive_type[sel_drive_type]['effector_allele']
        dfa = dfas[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfa = dfa[dfa[k] == v]
            dfa = dfa.drop(columns=[k], inplace=True)
        dfa = dfa[[svar0, svar1, ov_xvar, ov_yvar, 'Time', effallele]]
        dfa = dfa[dfa[svar0].isin(svvals[svar0]) &
                  dfa[svar1].isin(svvals[svar1]) &
                  dfa[ov_xvar].isin(svvals[ov_xvar]) &
                  dfa[ov_yvar].isin(svvals[ov_yvar])]
        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfa[var] = dfa[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfa, x='Time', y=effallele,
                      labels={
                          effallele: '',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-0.06, 1.06])
        return fig, 'shown', 'removed', None

    # ---- Wild type freq time series
    @callback(
        Output('wt-ts', 'figure'),
        Output('wt-ts', 'className'),
        Output('display-wt-ts', 'className'),
        Output('run-wt-ts', 'n_clicks'),
        [Input('run-wt-ts', 'n_clicks'),
         State('eir-itn7', 'value'),
         State('drive-type7', 'value'),
         State('outer-xvar7', 'value'),
         State('outer-yvar7', 'value'),
         State('sweep-var7-0', 'value'),
         State('sweep-var7-1', 'value'),
         ])
    @cache.memoize()
    def update_wt_ts(n_clicks, sel_eir_itn, sel_drive_type,
                     ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        wtallele = alleles_by_drive_type[sel_drive_type]['wt_allele']
        dfa = dfas[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfa = dfa[dfa[k] == v]
            dfa = dfa.drop(columns=[k], inplace=True)
        dfa = dfa[[svar0, svar1, ov_xvar, ov_yvar, 'Time', wtallele]]
        dfa = dfa[dfa[svar0].isin(svvals[svar0]) &
                  dfa[svar1].isin(svvals[svar1]) &
                  dfa[ov_xvar].isin(svvals[ov_xvar]) &
                  dfa[ov_yvar].isin(svvals[ov_yvar])]

        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfa[var] = dfa[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfa, x='Time', y=wtallele,
                      labels={
                          wtallele: '',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-0.06, 1.06])
        return fig, 'shown', 'removed', None

    # ---- Resistance freq time series
    @callback(
        Output('rs-ts', 'figure'),
        Output('rs-ts', 'className'),
        Output('display-rs-ts', 'className'),
        Output('run-rs-ts', 'n_clicks'),
        [Input('run-rs-ts', 'n_clicks'),
         State('eir-itn8', 'value'),
         State('drive-type8', 'value'),
         State('outer-xvar8', 'value'),
         State('outer-yvar8', 'value'),
         State('sweep-var8-0', 'value'),
         State('sweep-var8-1', 'value'),
         ])
    @cache.memoize()
    def update_rs_ts(n_clicks, sel_eir_itn, sel_drive_type,
                     ov_xvar, ov_yvar, svar0, svar1):
        if n_clicks is None:
            raise PreventUpdate
        # - Get selected data and sweep var vals
        svvals = sv_vals_by_drive_type[sel_drive_type]
        svdefs = sv_defs_by_drive_type[sel_drive_type]
        winame = fns_by_drive_type_eir_itn[sel_drive_type][sel_eir_itn]
        rsallele = alleles_by_drive_type[sel_drive_type]['resistance_allele']
        dfa = dfas[winame]

        # - Subset dataframe
        svdefsnow = {k: v for k, v in svdefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        for k, v in svdefsnow.items():
            dfa = dfa[dfa[k] == v]
            dfa = dfa.drop(columns=[k], inplace=True)
        dfa = dfa[[svar0, svar1, ov_xvar, ov_yvar, 'Time', rsallele]]
        dfa = dfa[dfa[svar0].isin(svvals[svar0]) &
                  dfa[svar1].isin(svvals[svar1]) &
                  dfa[ov_xvar].isin(svvals[ov_xvar]) &
                  dfa[ov_yvar].isin(svvals[ov_yvar])]
        for var in [svar0, svar1, ov_xvar, ov_yvar]:
            dfa[var] = dfa[var].astype(float).round(3)
        # - Plot
        fig = px.line(dfa, x='Time', y=rsallele,
                      labels={
                          rsallele: '',
                          'Time': 'Day',
                      },
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row="all", col="all")
        fig.add_vline(x=released_day, line_dash="dash", line_color="black",
                      row=0, col=len(ov_xvar) - 1, annotation_text="Vector <br>release",
                      annotation_position="top right", annotation_font_color="black")
        if 'with ITN' in sel_eir_itn:
            fig.add_vline(x=itn_distrib_days[1], line_dash="dot", line_color="forestgreen",
                          row=0, col=len(ov_xvar) - 1, annotation_text="ITN <br>distribs",
                          annotation_position="top right", annotation_font_color="forestgreen")
            for distrib_day in itn_distrib_days:
                fig.add_vline(x=distrib_day, line_dash="dot", line_color="forestgreen",
                              row="all", col="all")
        fig.update_xaxes(range=[0, num_yrs * 365])
        fig.update_yaxes(range=[-0.06, 1.06])
        return fig, 'shown', 'removed', None
