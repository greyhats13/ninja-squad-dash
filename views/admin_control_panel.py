import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from server import app, User
import users_mgt as um
import squad_reminder as sr
import pandas as pd
from datetime import datetime, timedelta

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_admin_control_panel', refresh=True),
                html.H5('Pilih dari menu di bawah ini :'),
                html.Button(
                    children='Tambahkan Squad',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_add-squad-button',
                    className="twelve columns",
                    style={
                        'background-color':'#138d75',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Squad Login Reminder',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_reminder-squad-button',
                    className="twelve columns",
                    style={
                        'background-color':'#e67e22',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Hapus Squad',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_delete-squad-button',
                    className="twelve columns",
                    style={
                        'background-color':'#c0392b',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Edit Holiday (Blocked Dates)',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_shipper-block-date-button',
                    className="twelve columns",
                    style={
                        'background-color':'#2980b9',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Generate Shipment Report',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_edit-shipment-report-button',
                    className="twelve columns",
                    style={
                        'background-color':'#8e44ad',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Br(),
                html.Hr(),
                html.H4("Must Updated More Often"),
                html.Button(
                    children='Unggah Data Shipment Terbaru',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_upload-data-button',
                    className="twelve columns",
                    style={
                        'background-color':'#c0392b',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Unggah Squad Terbaru',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_upload-new-squad-button',
                    className="twelve columns",
                    style={
                        'background-color':'#e67e22',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                ),
                html.Button(
                    children='Unggah Shipper Terbaru',
                    n_clicks=0,
                    type='submit',
                    id='admin_cp_upload-new-shipper-button',
                    className="twelve columns",
                    style={
                        'background-color':'#138d75',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '10px',
                    }
                )
            ]
        )
    ]
)

# Create callbacks
#
@app.callback(Output('url_admin_control_panel', 'pathname'),
              [Input('admin_cp_add-squad-button', 'n_clicks'),
              Input('admin_cp_reminder-squad-button', 'n_clicks'),
              Input('admin_cp_delete-squad-button', 'n_clicks'),
              Input('admin_cp_shipper-block-date-button', 'n_clicks'),
              Input('admin_cp_edit-shipment-report-button', 'n_clicks'),
              Input('admin_cp_upload-data-button', 'n_clicks'),
              Input('admin_cp_upload-new-squad-button', 'n_clicks'),
              Input('admin_cp_upload-new-shipper-button', 'n_clicks')])
def logout_dashboard(klik_tambah, klik_ingatkan, klik_hapus, klik_liburan, klik_shipment, klik_upload, klik_squad, klik_shipper):
    if klik_tambah > 0:
        return '/admin-add-user'
    if klik_hapus > 0:
        return '/admin-delete-user'
    if klik_liburan > 0:
        return '/admin-holiday-date'
    if klik_shipment > 0:
        return '/admin-edit-shipment'
    if klik_upload > 0:
        return '/admin-upload-data'
    if klik_squad > 0:
        return '/admin-database-squad'
    if klik_shipper > 0:
        return '/admin-database-shipper'
    if klik_ingatkan > 0:
        something_bad_happened = 0
        list = um.send_reminder()
        penerima = pd.DataFrame(list)
        penerima.columns = ['Fullname','Email','Last Login (Days)','Token']
        penerima['Last Login (Days)'] = penerima['Last Login (Days)'].apply(lambda x: (datetime.now()+timedelta(hours=7)-datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')).days if x!=None else None)
        filter_penerima = penerima[(penerima['Last Login (Days)']>=7) | (penerima['Last Login (Days)'].isna())]
        filter_penerima['Last Login (Days)'].fillna(value=pd.np.nan, inplace=True)
        for i, email in enumerate(filter_penerima['Email']):
            try:
                sr.kirimemail(email, filter_penerima['Fullname'].iloc[i], filter_penerima['Last Login (Days)'].iloc[i], filter_penerima['Token'].iloc[i])
            except:
                something_bad_happened = 1
                pass
        if something_bad_happened == 1:
            return '/admin-success-w-exc'
        else:
            return '/admin-success'
