import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html

from flask_login import current_user
from dash.dependencies import Input, Output, State
import datetime
import users_mgt as um
from server import app, User

warnings.filterwarnings("ignore")

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_squad_home', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="bingkaisalamun",
                            children=[
                                html.Div(className="row",
                                    children=[
                                        html.Img(
                                            src='assets/squad.webp',
                                            className="two columns",
                                            style={'max-width': '30%'}
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(id='home_sapasquad'),
                                                html.Div('Siap melihat perkembangan Anda?')
                                            ], className="ten columns"
                                        )
                                    ]
                                ),
                                html.P('', style={'margin-bottom' : '8px'}),
                                html.Div(
                                    children=[
                                        html.Button(
                                            children='Sales Coach',
                                            n_clicks=0,
                                            type='submit',
                                            id='home_salescoach-button',
                                            className="six columns",
                                            style={'background-color':'#218c74', 'color':'white'}
                                        ),
                                        html.Button(
                                            children='Ninja Squad',
                                            n_clicks=0,
                                            type='submit',
                                            id='home_squad-button',
                                            className="six columns",
                                            style={'background-color':'#2c2c54', 'color':'white'}
                                        )
                                    ], className="row"
                                ),
                            ]
                        ),

                        # html.P('Ini adalah hasil perolehan Anda selama ini (data terakhir diperbarui pada '+data['order_creation_datetime'].max().strftime('%d %B %Y')+'):', style={'text-align':'center'}),
                    ]
                )
            )
        ]
    ),
])


# Create callbacks
@app.callback(Output('url_squad_home', 'pathname'),
              [Input('home_salescoach-button', 'n_clicks'),
              Input('home_squad-button', 'n_clicks')])
def pilih_menu(klik_coach,klik_squad):
    if klik_coach > 0:
        return '/salescoach'
    if klik_squad > 0:
        return '/ninjasquad'

@app.callback(
    Output('home_sapasquad', 'children'),
    [Input('user-name', 'children')])
def notif_squad(input1):
    squad = current_user.username
    nama = current_user.fullname
    waktu = str(datetime.datetime.now()+datetime.timedelta(hours=7))
    um.delete_token(current_user.email, waktu)
    return html.H5('Apa kabar, '+nama+'?')
