# index page
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app, server, User
from flask_login import logout_user, current_user
from views import squad_home, login, login_fd, logout, nope, squad, control_panel, success_change_pw, admin_login, admin_add_user, admin_delete_user, admin_success, admin_success_exception, admin_failed, admin_control_panel, forgot_password, get_token, change_password, admin_holiday_date, edit_shipment_report, admin_upload_data, admin_database_shipper, admin_dashboard, admin_database_squad #ini dari folder views
from werkzeug.security import check_password_hash

from datetime import datetime

app.title = 'SquaDash - NinjaXpress'

header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.A([
                html.Img(
                    src='assets/logo.webp',
                    className='logo'
                )
            ], href="/"),
            html.Div(className='links', children=[
                html.A(id='user-name', className='link', href='/control-panel'),
                html.Div(id='logout', className='link')
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_dashboard.layout
            else:
                return squad_home.layout
        else:
            return login.layout
    elif pathname == '/login':
        if current_user.is_authenticated:
            return squad_home.layout
        else:
            return login.layout
    elif pathname == '/homesquad':
        if current_user.is_authenticated:
            return squad_home.layout
        else:
            return login_fd.layout
    elif pathname == '/ninjasquad':
        if current_user.is_authenticated:
            return squad.layout
        else:
            return login_fd.layout
    elif pathname == '/control-panel':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_control_panel.layout
            else:
                return control_panel.layout
        else:
            return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    elif pathname == '/hurray':
        if current_user.is_authenticated:
            return success_change_pw.layout
        else:
            return login_fd.layout
    elif pathname == '/forgotpassword':
        return forgot_password.layout
    elif pathname == '/adminlogindashboard':
        if current_user.is_authenticated:
            return nope.layout
        else:
            return admin_login.layout
    elif pathname == '/admin-dashboard':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_dashboard.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-add-user':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_add_user.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-success':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_success.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-upload-data':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_upload_data.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-edit-shipment':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return edit_shipment_report.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-database-shipper':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_database_shipper.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-database-squad':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_database_squad.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-success-w-exc':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_success_exception.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-failed':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_failed.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/admin-delete-user':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_delete_user.layout
            else:
                return nope.layout
        else:
            return nope.layout
    elif pathname == '/get-token':
        if current_user.is_authenticated:
            return nope.layout
        else:
            return get_token.layout
    elif pathname == '/admin-holiday-date':
        if current_user.is_authenticated:
            if current_user.username=="admin":
                return admin_holiday_date.layout
            else:
                return nope.layout
        else:
            return nope.layout
    else:
        try :
            user = User.query.filter_by(confirmkey=pathname[1:]).first()
            if user != None:
                return change_password.layout
            else:
                return nope.layout
        except:
            return nope.layout


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        if current_user.username=="admin":
            return html.Div(children=[html.Div('Anda masuk sebagai: ' + current_user.username),html.Div('(Klik di sini untuk masuk control panel)', style={'font-size':'12px', 'letter-spacing':'0'})], className='change-pw')
        else:
            return html.Div(children=[html.Div('Anda masuk sebagai: ' + current_user.username),html.Div('(Klik di sini untuk mengubah kata sandi)', style={'font-size':'12px', 'letter-spacing':'0'})], className='change-pw')
        # 'User authenticated' return username in get_id()
        # return username in get_id()
    else:
        return ''

@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Keluar', href='/logout', className='button')
    else:
        # return html.A('Daftar Sebagai Squad', href='/register', className='button', style={'background-color':'#2980b9', 'color':'white', 'border-radius':'30'})
        return ''

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
