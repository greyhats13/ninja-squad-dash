# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_admin_success', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                children=[
                    html.Img(
                        src='assets/senang.png',
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
                                    html.H5('Berhasil mengubah database!'),
                                    html.Div('Kembali ke Control Panel dengan menekan tombol di bawah.')
                                ], style={'text-align': 'center', 'line-height':'17px'}
                            )
                        ]
                    ),
                    html.Div(
                        # className="two columns",
                        # children=html.A(html.Button('LogOut'), href='/')
                        children=[
                            html.Button(id='admin_success-back-button',
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
@app.callback(Output('url_admin_success', 'pathname'),
              [Input('admin_success-back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/control-panel'
