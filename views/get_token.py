import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from server import app, User
from flask_login import login_user
import datetime
import users_mgt as um

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_token', refresh=True),
                html.H5('Masukkan token yang Anda peroleh dari email di inbox atau spam, atau klik link tombol yang diberikan pada email Anda:'),
                html.Div(
                    className="row",
                    children=[
                        dcc.Input(
                            placeholder='Masukkan Token Anda',
                            type='text',
                            id='tokenanda',
                            n_submit=0,
                            className="twelve columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),
                html.Div(children='', id='token_ada-salah', style={'padding-bottom':'12'}),

                html.Div(
                    children=[
                        html.Button(
                            children='Lanjutkan',
                            n_clicks=0,
                            type='submit',
                            id='token_submit-button',
                            className="twelve columns",
                            style={
                                'background-color':'#138d75',
                                'color':'white',
                                'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto'
                            }
                        )
                    ]
                ),

                # Getting password section
                html.Div(
                    id="gantipasswordnya",
                    style={'display':'none'},
                    className="row",
                    children=[
                        html.Hr(),

                        html.Hr(),

                        html.Div('Silakan masukkan kata sandi baru yang Anda inginkan:', style={'margin-bottom':'8px'}),

                        html.Div(
                            className="row",
                            children=[
                                html.Div('Kata sandi baru:', style={'font-weight':'bold'}, className='five columns'),
                                dcc.Input(
                                    placeholder='Masukkan kata sandi baru:',
                                    type='password',
                                    id='token_newpwd-box',
                                    n_submit=0,
                                    className="seven columns",
                                    style={'margin-bottom':'8px'}
                                )
                            ]
                        ),

                        html.Div(
                            className="row",
                            children=[
                                html.Div('Konfirmasi kata sandi baru:', style={'font-weight':'bold'}, className='five columns'),
                                dcc.Input(
                                    placeholder='Masukkan lagi kata sandi baru:',
                                    type='password',
                                    id='token_newpwdconfirm-box',
                                    n_submit=0,
                                    className="seven columns",
                                    style={'margin-bottom':'8px'}
                                )
                            ]
                        ),

                        html.Div(children='', id='token_salah-input-pw'),

                        html.Div(
                            children=[
                                html.Button(
                                    children='Ganti Kata Sandi',
                                    n_clicks=0,
                                    type='submit',
                                    id='token_change-pw-button',
                                    className="twelve columns",
                                    style={
                                        'background-color':'#138d75',
                                        'color':'white',
                                        'display': 'block',
                                        'margin-left': 'auto',
                                        'margin-right': 'auto',
                                        'margin-top': '12px'
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Create callbacks
#
@app.callback([Output('token_ada-salah', 'children'),
            Output('url_token', 'pathname'),
            Output('gantipasswordnya', 'style'),
            Output('token_salah-input-pw','children')],
              [Input('token_submit-button', 'n_clicks'),
              Input('tokenanda', 'n_submit'),
              Input('token_change-pw-button', 'n_clicks'),
              Input('token_newpwd-box', 'n_submit'),
              Input('token_newpwdconfirm-box', 'n_submit')],
              [State('tokenanda', 'value'),
              State('token_newpwd-box', 'value'),
              State('token_newpwdconfirm-box', 'value')])
def update_output(klik_token,enter_token,klik_password,enter_pw1,enter_pw2,inputtoken,inputpw1,inputpw2):
    user = User.query.filter_by(confirmkey=inputtoken).first()
    if (klik_password > 0) or (enter_pw1 > 0) or (enter_pw2 > 0):
        if str(inputpw1) == str(inputpw2) :
            if ((inputpw1==None) & (inputpw2==None)) or ((inputpw1=='') & (inputpw2=='')):
                return 'Token berhasil divalidasi. Lanjutkan proses pergantian kata sandi melalui form di bawah.', None, {'display': 'block'}, 'Kata sandi baru tidak boleh kosong'
            else:
                um.change_password(user.username,inputpw2)
                login_user(user)
                waktu = str(datetime.datetime.now()+datetime.timedelta(hours=7))
                um.delete_token(user.email, waktu)
                return 'Token berhasil divalidasi. Lanjutkan proses pergantian kata sandi melalui form di bawah.', '/hurray', {'display': 'block'}, ''
        else :
            return 'Token berhasil divalidasi. Lanjutkan proses pergantian kata sandi melalui form di bawah.', None, {'display': 'block'}, 'Kata sandi baru Anda dan konfirmasinya tidak cocok'
    if (klik_token > 0) or (enter_token > 0):
        if inputtoken != None:
            if user == None:
                return 'Token yang Anda masukkan salah.', None, {'display': 'none'}, ''
            else:
                return 'Token berhasil divalidasi. Lanjutkan proses pergantian kata sandi melalui form di bawah.', None, {'display': 'block'}, ''
        else :
            return 'Token masih kosong. Masukkan token yang Anda peroleh melalui email yang terdaftar.', None, {'display': 'none'}, ''
    else:
        return '', None, {'display': 'none'}, ''
