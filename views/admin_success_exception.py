# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_admin_success_exc', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                children=[
                    html.Img(
                        src='assets/senang.webp',
                        style={
                            'max-width': '30%',
                            'display': 'block',
                            'margin-left': 'auto',
                            'margin-right': 'auto'
                        },
                        className='row'
                    ),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="twelve columns",
                                children=[
                                    html.Br(),
                                    html.H5('Berhasil mengubah database dengan beberapa pengecualian!'),
                                    html.Div("""Sepertinya masalah ini terjadi karena ada email
                                    yang ga valid dari input yang dimasukkan. Untuk baris data tersebut,
                                    Ryo melakukan skip, jadi squad baru dengan email itu belum dapat pemberitahuan.
                                    Harap untuk memastikan bahwa data yang Anda masukkan benar.""")
                                ], style={'text-align': 'center', 'line-height':'17px'}
                            )
                        ]
                    ),
                    html.Div(
                        # className="two columns",
                        # children=html.A(html.Button('LogOut'), href='/')
                        children=[
                            html.Button(id='admin_successexc-back-button',
                                children='Kembali ke Control Panel',
                                n_clicks=0,
                                style={
                                    'margin-top':'20px',
                                    'display': 'block',
                                    'margin-left': 'auto',
                                    'margin-right': 'auto',
                                    'background-color':'#a93226',
                                    'color':'white'
                                }, className="row")
                            ]
                    )
                    ]
                )
            ]
        )
])


# Create callbacks
@app.callback(Output('url_admin_success_exc', 'pathname'),
              [Input('admin_successexc-back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/control-panel'
