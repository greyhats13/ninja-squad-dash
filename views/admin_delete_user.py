import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import users_mgt as um

from dash.dependencies import Input, Output, State

from server import app

warnings.filterwarnings("ignore")

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_admin_del_user', refresh=True),
    html.Div(id='trigger', style={'display':'none'}),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(className="bingkaiteks",
                            children=[
                                html.H5("Hapus Squad")
                            ],
                            style={
                            'text-align': 'center',
                            'padding-top': '10px',
                            'margin-bottom': '12px'
                        })
                    ]
                )
            ),
            dcc.Dropdown(
                id='admin_pilih-del-squad',
                multi=True,
                ),
            html.Div(
                className="row",
                children=[
                    html.Button(
                        children='Hapus Squad',
                        n_clicks=0,
                        type='submit',
                        id='admin_delete-squad-button',
                        className="twelve columns",
                        style={'background-color':'#a93226', 'color':'white'}
                    )
                ]
            )
        ]
    )
])

#
@app.callback(
    Output('admin_pilih-del-squad', 'options'),
    [Input('trigger', 'children')])
def display_outsput(input):
    squadlist = um.show_users()
    return [{'label': item[0], 'value': item[1]} for item in squadlist]

@app.callback(
    Output('admin_pilih-del-squad', 'value'),
    [Input('admin_pilih-del-squad', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('url_admin_del_user', 'pathname'),
    [Input('admin_pilih-del-squad', 'value'),
    Input('admin_delete-squad-button','n_clicks')])
def delete_user(userlist, klik_hapus):
    if klik_hapus > 0:
        for user in userlist:
            um.del_user(user)
        return '/admin-success'
