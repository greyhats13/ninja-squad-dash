import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from datetime import datetime
from server import app, User

import send_mail as sm

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_forgot_password', refresh=True),
                html.H5('''Masukkan email Anda yang terdaftar sebagai Ninja Squad untuk mengatur ulang sandi Anda:''', id='h1'),
                # html.Br(),
                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        dcc.Input(
                            placeholder='Masukkan Email Anda',
                            type='email',
                            id='emailanda',
                            n_submit=0,
                            className="twelve columns",
                            style={'margin-bottom':'8px'}
                        )
                    ]
                ),
                html.Div(children='', id='fp_ada-salah', style={'padding-bottom':'12'}),

                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        html.Button(
                            children='Lanjutkan',
                            n_clicks=0,
                            type='submit',
                            id='fp_submit-button',
                            className="six columns",
                            style={'background-color':'#138d75', 'color':'white'}
                        ),
                        html.Button(
                            children='Batal',
                            n_clicks=0,
                            type='submit',
                            id='fp_back-button',
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
@app.callback([Output('fp_ada-salah', 'children'),
            Output('url_forgot_password', 'pathname')],
              [Input('fp_submit-button', 'n_clicks'),
              Input('fp_back-button', 'n_clicks'),
              Input('emailanda', 'n_submit')],
              [State('emailanda', 'value')])
def update_output(klik_kirim, klik_batal, enter_kirim, inputemail):
    if klik_batal > 0:
        return None, '/'
    if (klik_kirim > 0) or (enter_kirim > 0):
        user = User.query.filter_by(email=inputemail.lower()).first()
        if user == None:
            return 'Tidak ditemukan akun yang terdaftar dengan email tersebut. Silakan hubungi admin untuk memproses lebih lanjut.', None
        else:
            token = sm.randomStringDigits(16)+inputemail.lower().split('@')[0]+'&'+user.username
            fullname = user.fullname
            return sm.kirimemail(inputemail.lower(), token, fullname), '/get-token'
    else:
        return '', None
