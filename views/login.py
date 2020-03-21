import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime
from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash

import users_mgt as um

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_login', refresh=True),
                html.Div(id='salamgambar'),
                html.Div(id='salamtulisan'),
                html.Div('''Harap log in dengan memasukkan email dan password untuk melanjutkan ke dashboard:''', id='h1'),
                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        dcc.Input(
                            placeholder='Masukkan email Anda',
                            type='email',
                            n_submit=0,
                            id='email-box',
                            className="four columns"
                        ),
                        dcc.Input(
                            placeholder='Masukkan kata sandi',
                            type='password',
                            id='pwd-box',
                            n_submit=0,
                            className="four columns"
                        ),
                        html.Button(
                            children='Login',
                            n_clicks=0,
                            type='submit',
                            id='login-button',
                            className="four columns",
                            style={'background-color':'#138d75', 'color':'white'}
                        ),
                        html.Div(children='', id='output-state')
                    ]
                ),
            ]
        )
    ]
)

@app.callback([Output('salamgambar', 'children'),
                Output('salamtulisan','children')],
              [Input('url_login', 'pathname')])
def update_salam(input):
    jamskg = datetime.now().hour+7
    if (0 <= jamskg < 4) or (19 <= jamskg < 28) :
    	salam = 'Selamat malam'
    	gbrsalam = 'assets/malem.webp'
    if (7 <= jamskg < 11) or (jamskg >= 28) :
    	salam = 'Selamat pagi'
    	gbrsalam = 'assets/pagi.webp'
    if 11 <= jamskg < 15 :
    	salam = 'Selamat siang'
    	gbrsalam = 'assets/pagi.webp'
    if 15 <= jamskg < 19 :
    	salam = 'Selamat sore'
    	gbrsalam = 'assets/sore.webp'
    return html.Img(src=gbrsalam, style={'display': 'block', 'margin-left': 'auto',
                    'margin-right': 'auto', 'margin-bottom': '10px'},
                    className='twelve columns'), html.H2(salam+", Squad!", style={'text-align': 'center'})

@app.callback([Output('url_login', 'pathname'),
                Output('output-state', 'children')],
              [Input('login-button', 'n_clicks'),
              Input('email-box','n_submit'),
              Input('pwd-box','n_submit')],
              [State('email-box', 'value'),
               State('pwd-box', 'value')])
def sucess(n_clicks, uname_submit, pwd_submit, input1, input2):
    if (uname_submit > 0) or (n_clicks > 0) or (pwd_submit > 0):
        user = User.query.filter_by(email=input1.lower()).first()
        if user:
            if check_password_hash(user.password, input2):
                login_user(user)
                return '/homesquad', ''
            else:
                return None, ('Kata sandi salah.', html.A('Lupa kata sandi?', href='/forgotpassword'))
        else:
            return None, 'Mohon maaf, akun anda tidak terdaftar. Silakan hubungi Admin apabila ini adalah suatu kesalahan.'
    else:
        return None, ''
