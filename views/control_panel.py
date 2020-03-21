import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from server import app
from flask_login import current_user
from werkzeug.security import check_password_hash

import users_mgt as um

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_profile', refresh=True),
                html.Div('''Pada laman ini, anda dapat
                melakukan penggantian kata sandi Anda. Silakan masukkan kata sandi lama
                beserta kata sandi baru di bawah:''', style={'margin-bottom':'10px'}),
                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        html.Div('Kata sandi lama:', style={'font-weight':'bold','margin-bottom':'8px'}, className='five columns'),
                        dcc.Input(
                            placeholder='Masukkan kata sandi lama',
                            type='password',
                            id='profile_oldpwd-box',
                            n_submit=0,
                            className="seven columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),

                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        html.Div('Kata sandi baru:', style={'font-weight':'bold','margin-bottom':'8px'}, className='five columns'),
                        dcc.Input(
                            placeholder='Masukkan kata sandi baru',
                            type='password',
                            id='profile_newpwd-box',
                            n_submit=0,
                            className="seven columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),

                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        html.Div('Konfirmasi kata sandi baru:', style={'font-weight':'bold','margin-bottom':'8px'}, className='five columns'),
                        dcc.Input(
                            placeholder='Masukkan lagi kata sandi baru',
                            type='password',
                            n_submit=0,
                            id='profile_newpwdconfirm-box',
                            className="seven columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),
                html.Div(children='', id='profile_ada-salah-input'),

                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        html.Button(
                            children='Ganti Kata Sandi',
                            n_clicks=0,
                            type='submit',
                            id='profile_change-pw-button',
                            className="six columns",
                            style={'background-color':'#138d75', 'color':'white'}
                        ),
                        html.Button(
                            children='Batal',
                            n_clicks=0,
                            type='submit',
                            id='profile_cancel-button',
                            className="six columns",
                            style={'background-color':'#cb4335', 'color':'white'}
                        )
                    ]
                ),
            ]
        )
    ]
)

# Create callbacks
#
@app.callback([Output('profile_ada-salah-input', 'children'),
            Output('url_profile', 'pathname')],
              [Input('profile_change-pw-button', 'n_clicks'),
              Input('profile_cancel-button', 'n_clicks'),
              Input('profile_oldpwd-box', 'n_submit'),
              Input('profile_newpwd-box', 'n_submit'),
              Input('profile_newpwdconfirm-box', 'n_submit')],
              [State('profile_oldpwd-box', 'value'),
               State('profile_newpwd-box', 'value'),
               State('profile_newpwdconfirm-box', 'value')])
def update_output(klik_gantipw,klik_batalganti,enter_oldpw,enter_pw1,enter_pw2,input_oldpw,input_pw1,input_pw2):
    if klik_batalganti > 0:
        return None, '/'
    if (klik_gantipw > 0) or (enter_oldpw > 0) or (enter_pw1 > 0) or (enter_pw2 > 0):
        if check_password_hash(current_user.password, input_oldpw):
            if str(input_pw1) == str(input_pw2) :
                if ((input_pw1==None) & (input_pw2==None)) or ((input_pw1=='') & (input_pw2=='')):
                    return 'Kata sandi baru tidak boleh kosong', None
                else:
                    um.change_password(current_user.username,input_pw2)
                    return '', '/hurray'
            else :
                return 'Kata sandi baru Anda dan konfirmasinya tidak cocok', None
        else:
            return 'Kata sandi lama Anda salah', None
    else:
        return '', None
