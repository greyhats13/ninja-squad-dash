import warnings
# Dash configuration
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import numpy as np
import math
import datetime

import locale
import plotly.graph_objs as go
import plotly
from plotly.offline import *

from flask_login import current_user
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State

from server import app, User

warnings.filterwarnings("ignore")

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_admin_db', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(className="bingkaiteks",
                            children=[
                                html.H4("Tambahkan Squad")
                            ],
                            style={
                            'text-align': 'center'
                        })
                    ]
                ),

            )
        ]
    ),
])


# Create callbacks
# @app.callback(Output('url_login_success', 'pathname'),
#               [Input('bapakkoc', 'n_clicks'),
#               Input('skuattenaga', 'n_clicks')])
# def logout_dashboard(koc_clicks,skuy_clicks):
#     if koc_clicks > 0:
#         return '/salescoach'
#     if skuy_clicks > 0:
#         return '/ninjasquad'
