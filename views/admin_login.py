import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash


layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_adminlogin', refresh=True),
                html.Div('''Harap log in untuk melanjutkan ke dashboard:''', id='h1'),
                html.Div(
                    # method='Post',
                    className="row",
                    children=[
                        dcc.Input(
                            placeholder='Enter your username',
                            type='text',
                            n_submit=0,
                            id='admin_uname-box',
                            className="four columns"
                        ),
                        dcc.Input(
                            placeholder='Enter your password',
                            type='password',
                            n_submit=0,
                            id='admin_pwd-box',
                            className="four columns"
                        ),
                        html.Button(
                            children='Login',
                            n_clicks=0,
                            type='submit',
                            id='admin_login-button',
                            className="four columns",
                            style={'background-color':'#a93226', 'color':'white'}
                        ),
                        html.Div(children='', id='output-admin-state')
                    ]
                ),
            ]
        )
    ]
)

@app.callback([Output('url_adminlogin', 'pathname'),
                Output('output-admin-state', 'children')],
              [Input('admin_login-button', 'n_clicks'),
              Input('admin_uname-box', 'n_submit'),
              Input('admin_pwd-box', 'n_submit')],
              [State('admin_uname-box', 'value'),
               State('admin_pwd-box', 'value')])
def update_output(klik_login, enter_uname, enter_pw, input1, input2):
    if (klik_login > 0) or (enter_uname > 0) or (enter_pw > 0):
        user = User.query.filter_by(username=input1).first()
        if user.username=="admin":
            if check_password_hash(user.password, input2):
                login_user(user)
                return '/admin-dashboard',''
            else:
                return None, 'Terjadi kesalahan'
        else:
            return None, 'Terjadi kesalahan'
    else:
        return None, ''
