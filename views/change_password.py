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
                dcc.Location(id='url_change_password_token', refresh=True),
                html.Div(children='', id='cp_save-path', style={'display':'none'}),

                html.Div('Silakan masukkan kata sandi baru yang Anda inginkan:', style={'margin-bottom':'8px'}),

                html.Div(
                    className="row",
                    children=[
                        html.Div('Kata sandi baru:', style={'font-weight':'bold'}, className='five columns'),
                        dcc.Input(
                            placeholder='Masukkan kata sandi baru:',
                            type='password',
                            id='cp_newpwd-box',
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
                            id='cp_newpwdconfirm-box',
                            n_submit=0,
                            className="seven columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),

                html.Div(children='', id='cp_ada-salah-input'),

                html.Div(
                    children=[
                        html.Button(
                            children='Ganti Kata Sandi',
                            n_clicks=0,
                            type='submit',
                            id='cp_submit-change-pw-button',
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

# Create callbacks
#
@app.callback(Output('cp_save-path', 'children'),
              [Input('url_change_password_token', 'pathname')])
def save_the_urlpath(urlpath):
    return urlpath
#
@app.callback([Output('cp_ada-salah-input', 'children'),
            Output('url_change_password_token', 'pathname')],
              [Input('cp_submit-change-pw-button', 'n_clicks'),
              Input('cp_newpwd-box', 'n_submit'),
              Input('cp_newpwdconfirm-box', 'n_submit')],
              [State('cp_save-path','children'),
              State('cp_newpwd-box', 'value'),
              State('cp_newpwdconfirm-box', 'value')])
def update_output(klik_password,enter_pw1,enter_pw2,urlpath,inputpw1,inputpw2):
    user = User.query.filter_by(confirmkey=urlpath[1:]).first()
    if (klik_password > 0) or (enter_pw1 > 0) or (enter_pw2 > 0):
        if str(inputpw1) == str(inputpw2) :
            if ((inputpw1==None) & (inputpw2==None)) or ((inputpw1=='') & (inputpw2=='')):
                return 'Kata sandi baru tidak boleh kosong', None
            else:
                um.change_password(user.username,inputpw2)
                login_user(user)
                waktu = str(datetime.datetime.now()+datetime.timedelta(hours=7))
                um.delete_token(user.email, waktu)
                return '', '/hurray'
        else :
            return 'Kata sandi baru Anda dan konfirmasinya tidak cocok', None
    else:
        return '', None
