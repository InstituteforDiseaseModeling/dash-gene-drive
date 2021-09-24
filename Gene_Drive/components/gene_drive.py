import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

# -------- Choose experiment and set up params

# -- 1.) Spatial, integral, VC and GM, EIR = 30
# wi_name = 'spatialinside_integral2l4a_VC_and_GM_aEIR30_sweep_rc_d1_rr20_se2'
# wi_name_sh = 'spatial, integral drive, VC and GM, EIR = 30'
# distrib_itns = True
# num_sweep_vars = 4
# drive_type = 'integral'

# -- 2.) Spatial, classic, VC and GM, EIR = 30
wi_name = 'spatialinside_classic3allele_VC_and_GM_aEIR30_sweep_rc_d_rr0_sne'
wi_name_sh = 'spatial, classic drive, VC and GM, EIR = 30'
distrib_itns = True
num_sweep_vars = 4
drive_type = 'classic'

# -- 3.) Spatial, integral, GM only, EIR = 30
# wi_name = 'spatialinside_integral2l4a_GM_only_aEIR30_sweep_rc_d1_rr20_se2'
# wi_name_sh = 'spatial, integral drive, GM only, EIR = 30'
# distrib_itns = False
# num_sweep_vars = 4
# drive_type = 'integral'

# -- 4.) Spatial, classic, GM only, EIR = 30
# wi_name = 'spatialinside_classic3allele_GM_only_aEIR30_sweep_rc_d_rr0_sne_release_day_release_node_num'
# wi_name_sh = 'spatial, classic drive, GM only, EIR = 30'
# distrib_itns = False
# num_sweep_vars = 6
# drive_type = 'classic'

data_dir = 'csvs'

if distrib_itns == True:
    itn_distrib_days = [180, 3 * 365 + 180, 6 * 365 + 180]

released_mosqs = True
if released_mosqs == True:
    released_day = 180

num_yrs = 8  # length of sim
elim_day = 2555  # day on which elim fraction is calculated
num_seeds = 20  # num of seeds per sim

if num_sweep_vars == 6:
    if drive_type == 'classic':
        allvardefs = {'rc': 1, 'd': 1, 'rr0': 0, 'sne': 0,
                      'rd': 180, 'nn': 6}
        allvarvals = {'rc': [1, 0.9, 0.8, 0.7, 0.6, 0.5],
                      'd': [1, 0.95, 0.9],
                      'rr0': [0, 0.1, 0.2],
                      'sne': [0, 0.05, 0.1, 0.15, 0.2],
                      'rd': [180, 240, 300, 360, 420, 480, 545],
                      'nn': [6, 12]}
elif num_sweep_vars == 4:
    if drive_type == 'classic':
        allvardefs = {'rc': 1, 'd': 1, 'sne': 0, 'rr0': 0}
        allvarvals = {'rc': [1, 0.9, 0.8, 0.7, 0.6, 0.5],
                      'd': [1, 0.95, 0.9],
                      'rr0': [0, 0.1, 0.2],
                      'sne': [0, 0.05, 0.1, 0.15, 0.2]}
        allvarvals_fns = {'rc': [1, 0.9, 0.8, 0.7, 0.6, 0.5],
                          'd': [1, 0.95, 0.9],
                          'rr0': [0, 0.1, 0.2],
                          'sne': [0, 0.05, 0.1, 0.15, 0.2]}
    elif drive_type == 'integral':
        allvardefs = {'rc': 1, 'd1': 1, 'se2': 0, 'rr20': 0}
        allvarvals = {'rc': [1, 0.9, 0.8, 0.7, 0.6, 0.5],
                      'd1': [1, 0.95, 0.9],
                      'rr20': [0, 0.1, 0.2],
                      'se2': [0, 0.05, 0.1, 0.15, 0.2]}

##
# -------- Load data
dfi = pd.read_csv(os.path.join(data_dir, 'dfi_' + wi_name + '.csv'))
dfa = pd.read_csv(os.path.join(data_dir, 'dfa_' + wi_name + '.csv'))
dfe = pd.read_csv(os.path.join(data_dir, 'dfe_' + wi_name + '.csv'))
dfed = pd.read_csv(os.path.join(data_dir, 'dfed_' + wi_name + '.csv'))


class GeneDriveAIO(html.Div):
    def __init__(self):
        super().__init__([

            html.Div(
                id="tabs-content",
                style={"height": "100%"},
                children=[
                    dcc.Tabs([
                        dcc.Tab(label='Elimination probabilities',
                                style={"height": "100%"},
                                children=[
                                    html.Div(className="container-fluid",
                                             children=[html.H2(
                                                 className="text-center",
                                                 children='Elim probabilities: ' + wi_name_sh)]
                                             ),
                                    html.Div(
                                        className="container-fluid row",
                                        children=[
                                            html.Div(
                                                className="col-11",
                                                children=[
                                                    html.Div(
                                                        className="row",
                                                        children=[

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer x-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-xvar0',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rc'
                                                                    )
                                                                ]),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer y-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-yvar0',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='d'
                                                                    )
                                                                ]),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Matrix x-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='matrix-xvar0',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rr0')
                                                                ]),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Matrix y-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='matrix-yvar0',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='sne')
                                                                ]),

                                                        ])
                                                ]
                                            ),
                                            html.Div(
                                                className="col-1",
                                                children=[
                                                    html.Button(
                                                        className="btn btn-lg btn-primary btn-block",
                                                        children="Run",
                                                        id="run-elim-prob-matrices",
                                                        style={"height": "100%"},
                                                        n_clicks=0
                                                    )
                                                ]
                                            )
                                        ]
                                    ),

                                    html.Div([
                                        dcc.Graph(id='elim-prob-matrices',
                                                  style={'width': '100%', 'height': '60vh'})
                                    ])
                                ]),

                        dcc.Tab(label='Years to elimination',
                                style={"height": "100%"},
                                children=[
                                    html.Div(className="container-fluid",
                                             children=[html.H2(
                                                 className="text-center",
                                                 children='Years to elim: ' + wi_name_sh)]
                                             ),
                                    html.Div(
                                        className="container-fluid row",
                                        children=[
                                            html.Div(
                                                className="col-11",
                                                children=[
                                                    html.Div(
                                                        className="row",
                                                        children=[

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer x-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-xvar1',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rc'
                                                                    )
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer y-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-yvar1',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='d'
                                                                    )
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Matrix x-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='matrix-xvar1',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rr0')
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Matrix y-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='matrix-yvar1',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='sne')
                                                                ], style={'width': '10%'}),

                                                        ], style=dict(display='flex')
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                className="col-1",
                                                children=[
                                                    html.Button(
                                                        className="btn btn-lg btn-primary btn-block",
                                                        children="Run",
                                                        id="run-elim-day-matrices",
                                                        style={"height": "100%"},
                                                        n_clicks=0
                                                    )
                                                ]
                                            )
                                        ]
                                    ),

                                    html.Div([
                                        dcc.Graph(id='elim-day-matrices',
                                                  style={'width': '100%', 'height': '60vh'})
                                    ])
                                ]),

                        dcc.Tab(label='Prevalence time series',
                                style={"height": "100%"},
                                children=[
                                    html.Div(className="container-fluid",
                                             children=[html.H2(
                                                 className="text-center",
                                                 children='Prev time series: ' + wi_name_sh), ]
                                             ),
                                    html.Div(
                                        className="container-fluid row",
                                        children=[
                                            html.Div(
                                                className="col-11",
                                                children=[
                                                    html.Div(
                                                        className="row",
                                                        children=[
                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer x-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-xvar2',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rr0'
                                                                    )
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['Outer y-var:'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='outer-yvar2',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='sne'
                                                                    )
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['1st sweep var (color):'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='sweep-var2-0',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='rc')
                                                                ], style={'width': '10%'}),

                                                            html.Div(
                                                                className="col-3",
                                                                children=[
                                                                    html.Label(['2nd sweep var (line style):'],
                                                                               style={'font-weight': 'bold',
                                                                                      'text-align': 'center'}),
                                                                    dcc.Dropdown(
                                                                        id='sweep-var2-1',
                                                                        options=[{'label': i, 'value': i} for i in
                                                                                 list(allvarvals.keys())],
                                                                        value='d')
                                                                ], style={'width': '10%'}),

                                                        ],
                                                        style=dict(display='flex'))
                                                ]
                                            ),
                                            html.Div(
                                                className="col-1",
                                                children=[
                                                    html.Button(
                                                        className="btn btn-lg btn-primary btn-block",
                                                        children="Run",
                                                        id="run-prev-ts",
                                                        style={"height": "100%"},
                                                        n_clicks=0
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),

                                    html.Div([
                                        dcc.Graph(id='prev-ts',
                                                  style={'width': '100%', 'height': '60vh'})
                                    ])
                                ])
                    ])
                ])
        ])

    @callback(
        Output('elim-prob-matrices', 'figure'),
        [State('outer-xvar0', 'value'),
         State('outer-yvar0', 'value'),
         State('matrix-xvar0', 'value'),
         State('matrix-yvar0', 'value'),
         Input('run-elim-prob-matrices', 'n_clicks')])
    def update_elim_prob_matrices(ov_xvar, ov_yvar, mat_xvar, mat_yvar, n_clicks):
        # - Get all outer xvar and yvar vals
        ov_xvar_vals = allvarvals[ov_xvar]
        ov_yvar_vals = allvarvals[ov_yvar]

        # - Compute subplot titles and heatmaps
        iaxis = 1
        subplots = []
        subplot_titles = []

        for ov_yvar_val in ov_yvar_vals:
            for ov_xvar_val in ov_xvar_vals:

                # - Compute heatmap
                allvardefsnow = {k: v for k, v in allvardefs.items() if k not in [mat_xvar, mat_yvar, ov_xvar, ov_yvar]}
                dfenow = dfe
                for k, v in allvardefsnow.items():
                    dfenow = dfenow[dfenow[k] == v]
                    dfenow.drop(columns=[k], inplace=True)
                dfenow = dfenow[dfenow[ov_xvar] == ov_xvar_val]
                dfenow = dfenow[dfenow[ov_yvar] == ov_yvar_val]
                dfenow.drop(columns=[ov_xvar, ov_yvar], inplace=True)
                dfenownow = (dfenow.groupby([mat_xvar, mat_yvar])[
                                 'True_Prevalence_elim'].sum() / num_seeds).reset_index()
                matnow = dfenownow.pivot_table(index=[mat_yvar], columns=[mat_xvar], values='True_Prevalence_elim')

                # - Create annotated heatmap
                subplots.append(ff.create_annotated_heatmap(
                    z=matnow.values,
                    x=matnow.columns.tolist(),
                    y=matnow.index.tolist(),
                    zmax=1,
                    zmin=0,
                    # coloraxis='coloraxis',
                    # hovertemplate=mat_xvar + ': %{x}<br>' + mat_yvar + ': %{y}<br>Elim prob: %{z}<extra></extra>',
                    showscale=True,
                    colorscale='YlOrBr_r')
                )

                # - Update annotation axes
                for annot in subplots[-1]['layout']['annotations']:
                    annot['xref'] = 'x' + str(iaxis)
                    annot['yref'] = 'y' + str(iaxis)
                iaxis = iaxis + 1

                # - Create subplot titles
                # subplot_titles.append(ov_xvar + '=' + str(ov_xvar_val) + ', '
                #                      + ov_yvar + '=' + str(ov_yvar_val))

        # - Set up subplot framework and titles
        fig = make_subplots(
            rows=len(ov_yvar_vals), cols=len(ov_xvar_vals),
            # subplot_titles=subplot_titles,
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
            tickvals=allvarvals[mat_xvar],
            ticktext=[str(val) for val in allvarvals[mat_xvar]]
        )
        fig.update_yaxes(
            tickmode='array',
            tickvals=allvarvals[mat_yvar],
            ticktext=[str(val) for val in allvarvals[mat_yvar]]
        )
        # fig.update_coloraxes(colorscale='Viridis')
        fig.update_layout(margin=dict(l=60, r=50, b=50, t=30))
        #                   coloraxis={'colorscale': 'YlOrBr_r'},
        #                   title='Elim probabilities, ' + wi_name,
        #                   transition_duration=500)

        return fig

    @callback(
        Output('elim-day-matrices', 'figure'),
        [State('outer-xvar1', 'value'),
         State('outer-yvar1', 'value'),
         State('matrix-xvar1', 'value'),
         State('matrix-yvar1', 'value'),
         Input('run-elim-day-matrices', 'n_clicks')])
    def update_elim_day_matrices(ov_xvar, ov_yvar, mat_xvar, mat_yvar, n_clicks):
        # - Get all outer xvar and yvar vals
        ov_xvar_vals = allvarvals[ov_xvar]
        ov_yvar_vals = allvarvals[ov_yvar]

        # - Compute subplot titles and heatmaps
        iaxis = 1
        subplots = []

        for ov_yvar_val in ov_yvar_vals:
            for ov_xvar_val in ov_xvar_vals:

                # - Compute heatmap
                allvardefsnow = {k: v for k, v in allvardefs.items() if k not in [mat_xvar, mat_yvar, ov_xvar, ov_yvar]}
                dfednow = dfed
                for k, v in allvardefsnow.items():
                    dfednow = dfednow[dfednow[k] == v]
                    dfednow.drop(columns=[k], inplace=True)
                dfednow = dfednow[dfednow[ov_xvar] == ov_xvar_val]
                dfednow = dfednow[dfednow[ov_yvar] == ov_yvar_val]
                dfednow.drop(columns=[ov_xvar, ov_yvar], inplace=True)
                dfednow.loc[dfednow['True_Prevalence_elim'] == False,
                            'True_Prevalence_elim_day'] = np.nan
                dfednow.drop(columns=['True_Prevalence_elim'], inplace=True)
                dfednownow = (dfednow.groupby([mat_xvar, mat_yvar])['True_Prevalence_elim_day'].mean()).reset_index()
                matnow = dfednownow.pivot_table(index=[mat_yvar], columns=[mat_xvar],
                                                values='True_Prevalence_elim_day', dropna=False)
                # matnow = matnow.round(1)  # .astype('Int64')
                matnow = (matnow / 365).round(1)  # .astype('Int64')
                # z_text = [[str(y) for y in x] for x in matnow.values]

                # - Create annotated heatmap
                subplots.append(ff.create_annotated_heatmap(
                    z=matnow.values,
                    x=matnow.columns.tolist(),
                    y=matnow.index.tolist(),
                    # annotation_text=z_text,
                    zmax=(dfed['True_Prevalence_elim_day'] / 365).max(),
                    zmin=(dfed['True_Prevalence_elim_day'] / 365).min(),
                    showscale=True,
                    colorscale='YlOrBr')
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
            ticklen=10,
            tickmode='array',
            tickvals=allvarvals[mat_xvar],
            ticktext=[str(val) for val in allvarvals[mat_xvar]]
        )
        fig.update_yaxes(
            ticklen=10,
            tickmode='array',
            tickvals=allvarvals[mat_yvar],
            ticktext=[str(val) for val in allvarvals[mat_yvar]]
        )
        fig.update_layout(margin=dict(l=60, r=50, b=50, t=30))

        return fig

    @callback(
        Output('prev-ts', 'figure'),
        [State('outer-xvar2', 'value'),
         State('outer-yvar2', 'value'),
         State('sweep-var2-0', 'value'),
         State('sweep-var2-1', 'value'),
         Input('run-prev-ts', 'n_clicks')])
    def update_prev_ts(ov_xvar, ov_yvar, svar0, svar1, n_clicks):
        allvardefsnow = {k: v for k, v in allvardefs.items() if k not in [svar0, svar1, ov_xvar, ov_yvar]}
        dfinow = dfi
        for k, v in allvardefsnow.items():
            dfinow = dfinow[dfinow[k] == v]
            dfinow.drop(columns=[k], inplace=True)

        fig = px.line(dfinow, x='Time', y='PfHRP2 Prevalence',
                      color=svar0, line_dash=svar1,
                      facet_col=ov_xvar, facet_row=ov_yvar)
        return fig
