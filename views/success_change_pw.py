# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_success_change_pw', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                children=[html.Img(
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
                                html.H5('Hore, kamu telah berhasil mengubah kata sandi!'),
                                html.Div('Klik tombol di bawah untuk menuju ke beranda Anda.')
                            ], style={'text-align': 'center', 'line-height':'17px'}
                        )
                    ]
                ),
                html.Div(
                    # children=html.A(html.Button('LogOut'), href='/')
                    children=[
                        html.Button(id='scp_back-button',
                            children='Menuju ke Beranda',
                            n_clicks=0,
                            style={
                                'margin-top':'20px',
                                'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto',
                                'background-color':'#138d75',
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
@app.callback(Output('url_success_change_pw', 'pathname'),
              [Input('scp_back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
