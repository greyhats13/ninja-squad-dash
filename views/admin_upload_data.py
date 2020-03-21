import dash_core_components as dcc
import dash_html_components as html
import time
import requests
import pandas as pd
from dash.dependencies import Input, Output, State
import os
import base64
import numpy as np
import io
from server import app, server
from datetime import datetime, timedelta
from six.moves.urllib.parse import quote
import csv
import re
# ----------------------------- Function Definitions -----------------------------#
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df

insensitive_ns = re.compile(re.escape('(ninja squad)'), re.IGNORECASE)

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_upload_data', refresh=True),
                html.H3('Upload New Squad Data', style={'text-align':'center'}),
                html.Div(id='shipment_subtitle', style={'text-align':'center'}),
                dcc.Upload(
                    id='upload-data',
                    className="twelve columns",
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin-bottom': '12px'
                    }, multiple=False),
                html.Div(id='hasil', style={'text-align': 'center'}),
                html.Br(),
                html.Hr(),

                html.H3('Pull Uncompleted Data', style={'text-align':'center'}),
                html.Button(
                    id='pull_data_button',
                    n_clicks=0,
                    type='submit',
                    className="twelve columns",
                    children='Pull Data',
                    style={'background-color':'#138d75',
                    'color':'white',
                    'display': 'block',
                    'margin-left': 'auto',
                    'margin-right': 'auto',
                    'margin-top': '12px'}
                    ),
                html.Div(id='hasil_pull', style={'text-align': 'center'}),
            ]
        )
    ]
)

@app.callback(
    Output('hasil_pull', 'children'),
    [Input('pull_data_button', 'n_clicks')])
def pull_data(klik_edit_shipment):
    if klik_edit_shipment > 0:
        data_unc = pd.read_pickle('./data/data.pkl')
        data_unc = data_unc[~data_unc.granular_status.isin(['Completed','Cancelled','Returned to Sender'])][["tracking_id"]].apply(lambda x: "'"+x+"',")
        with open("./data/query.txt") as file:
            query = file.read()
        query = query.replace('{{placeholder}}',data_unc.to_csv(index=False, header=False, quoting=csv.QUOTE_NONE, escapechar=" ")[:-3])
        query = "data:text/plain;charset=utf-8,%EF%BB%BF" + quote(query)

        return (html.A('Klik di sini buat generate query untuk narik datanya.', href=query, target="_blank"), ' Setelah dicopy, bisa dipaste ke text box (hapus dulu textboxnya biar kosong) yang ada di ', html.A('link ini, lalu klik Tombol Execute', href='https://redash.ninjavan.co/queries/6064/source', target="_blank"), '. Lalu, download as Excel atau CSV, dan upload lewat tombol di atas.')

@app.callback(
    [Output('shipment_subtitle', 'children'),
    Output('hasil', 'children')],
    [Input('upload-data', 'filename'),
    Input('upload-data', 'contents'),
    Input('url_upload_data','pathname')])
def update_output(filename,contents,trigger):
    kode = pd.read_pickle('./data/kodepos.pkl')
    sla = pd.read_pickle('./data/order_sla.pkl')
    holiday = pd.read_pickle('./data/holiday.pkl')
    data_wh = pd.read_pickle('./data/data.pkl')
    with open("./data/query_shipment.txt") as file:
        query_shipment = file.read()
    if contents is not None:
        try:
            data = parse_contents(contents, filename)
            data['order_creation_datetime'] = pd.to_datetime(data['order_creation_datetime'])
            data['first_inbound_datetime'] = pd.to_datetime(data['first_inbound_datetime'])
            data['pod_datetime'] = pd.to_datetime(data['pod_datetime'])
            data['first_attempt_at'] = pd.to_datetime(data['first_attempt_at'])
            data['last_attempt_at'] = pd.to_datetime(data['last_attempt_at'])
            data.shipper_name = data.shipper_name.apply(lambda x: insensitive_ns.sub('',x))
            data.to_postcode = data.to_postcode.astype('str').apply(lambda s: (s.encode('ascii', 'ignore')).decode("utf-8"))
            data.to_postcode = pd.to_numeric(data.to_postcode, errors='coerce').fillna(0).astype(int)
            data = pd.merge(data,kode,on='to_postcode',how='left')
            data.submitted_weight = data.submitted_weight.replace('\n"',"",regex=True)
            data['first_attempt_date'] = data.first_attempt_at.dt.date.astype(str)

            data = pd.merge(data,sla,on=['from_billing_zone','to_billing_zone','service_type'], how='left')

            temp = [np.nan]*len(data)

            for i in range(len(data)):
                if data.granular_status[i] != "Cancelled" :
                    if pd.isnull(data.inbound_cutoff[i]) == True :
                        pass
                    else :
                        if pd.isnull(data.first_attempt_at[i]) == True :
                            temp[i] = np.busday_count(data.inbound_cutoff[i], datetime.today().strftime('%Y-%m-%d'), weekmask='1111110', holidays=list(holiday.date))
                        else :
                            temp[i] = np.busday_count(data.inbound_cutoff[i], data.first_attempt_date[i], weekmask='1111110', holidays=list(holiday.date))

            data['delivery_duration'] = pd.Series(temp, index=data.index)
            conditions = [data.delivery_duration<=data.service_days,data.service_days.isna(),data.delivery_duration.isna()]
            choices = ['hit', '','']
            data['hit/miss'] = np.select(conditions, choices, default='miss')

            # data = data.drop(['delivery_fee_origin','first_attempt_date'], axis=1)

            data_wh = pd.concat([data_wh,data], sort=False)
            data_wh = data_wh.drop_duplicates('tracking_id',keep='last')
            data_wh = data_wh.sort_values(by='order_creation_datetime').reset_index(drop=True)
            data_wh.to_pickle('./data/data.pkl')
            query_shipment = query_shipment.replace('{{placeholder_start}}',str(data_wh.order_creation_datetime.max().date()+timedelta(days=1)))
            query_shipment = query_shipment.replace('{{placeholder_end}}',(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d'))
            query_shipment = "data:text/plain;charset=utf-8,%EF%BB%BF" + quote(query_shipment)
            return ('Data tanggal terakhir di database : ' + str(data_wh.order_creation_datetime.max().date()) + ". ", html.A('Klik di sini buat generate query untuk narik data terbaru.', href=query_shipment, target="_blank")), 'Sudah selesai nambah data dari tanggal '+str(data.order_creation_datetime.min().date())+' sampai '+str(data.order_creation_datetime.max().date())+' gannnn.'
        except Exception as ex:
            query_shipment = query_shipment.replace('{{placeholder_start}}',str(data_wh.order_creation_datetime.max().date()+timedelta(days=1)))
            query_shipment = query_shipment.replace('{{placeholder_end}}',(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d'))
            query_shipment = "data:text/plain;charset=utf-8,%EF%BB%BF" + quote(query_shipment)
            return ('Data tanggal terakhir di database : ' + str(data_wh.order_creation_datetime.max().date()) + ". ", html.A('Klik di sini buat generate query untuk narik data terbaru.', href=query_shipment, target="_blank")), 'Hmmm, bingung euy, ada error. Coba cek datanya dulu. Error : '+str(ex)
    else:
        query_shipment = query_shipment.replace('{{placeholder_start}}',str(data_wh.order_creation_datetime.max().date()+timedelta(days=1)))
        query_shipment = query_shipment.replace('{{placeholder_end}}',(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d'))
        query_shipment = "data:text/plain;charset=utf-8,%EF%BB%BF" + quote(query_shipment)
        return ('Data tanggal terakhir di database : ' + str(data_wh.order_creation_datetime.max().date()) + ". ", html.A('Klik di sini buat generate query untuk narik data terbaru.', href=query_shipment, target="_blank")), ''
