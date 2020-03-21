import warnings
# Dash configuration
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import math
import datetime
from random import randint
import numpy as np
import users_mgt as um

import base64
import io

# import locale
import plotly.graph_objs as go
import plotly
from plotly.offline import *

from babel.numbers import format_currency
from flask_login import current_user
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State

from server import app, User

warnings.filterwarnings("ignore")

# databaru['coach'] = temp.apply(lambda x:x[2] if len(x)==4 else "coach-itself")
granularstatus = ["Arrived at Origin Hub", "Arrived at Sorting Hub", "Cancelled", "Completed", "Customs Cleared", "En-route to Sorting Hub", "On Hold", "On Vehicle for Delivery", "Pending Pickup", "Pending Pickup at Distribution Point", "Pending Reschedule", "Pickup fail", "Returned to Sender", "Staging", "Transferred to 3PL", "Van en-route to pickup"]

#create summary Bar
def admin_bikin_barchart(dff, dateline, aggregation):
    data_x = dateline['period']
    data_y_vol = pd.merge(dateline['order_creation_datetime'], dff, how='left')['Volume'].fillna('None')
    data_y_money = pd.merge(dateline['order_creation_datetime'], dff, how='left')['Biaya Pengiriman'].fillna('None')
    return {
        'data': [go.Bar(
            x=data_x,
            y=data_y_vol,
            text=data_y_vol,
            textposition = 'auto',
            name = 'Volume',
            marker=dict(
                color='#130f60',
                line=dict(
                    color='#130f40',
                    width=1.5),
                    ),
            opacity=0.8
            ),
            go.Scatter(
                x=data_x,
                y=data_y_money,
                name='Biaya',
                yaxis='y2',
                line = dict(color = '#20bf6b', width = 1.85),
                opacity=0.8
            )],
        'layout': {
            'autosize': True,
            'showlegend': False,
            # 'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False,'showline': True, 'showticklabels':True, 'title':'Periode','ticks':'outside'},
            'yaxis': {'showgrid': True,'showline': True, 'zeroline':False, 'showticklabels':True, 'title':'Total Order'},
            'yaxis2': {'showgrid': True,'showline': True, 'zeroline':False, 'showticklabels':True, 'title':'Biaya Pengiriman', 'overlaying':'y', 'side':'right'},
            'title': 'Ninja Squad Progress'
        }
    }

def get_col_widths(dataframe):
    # Menentukan panjang maksimum dari kolom index
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Menggabungkan maksimum dari panjang kolom dan panjang data dari kolom tersebut
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

#create line chart
def admin_bikin_grafik_shipper(shipper_name, dataship, dateline, section):
    # change title for y axis
    if section=="Volume":
        y_title = "Total Shipment"
    else:
        y_title = "Biaya Pengiriman"
    traces = []
    for i in shipper_name :
        index_name = dataship[dataship['ID Shipper']==i]['Nama Shipper'].iloc[0]
        data_y = pd.merge(dateline['order_creation_datetime'], dataship[dataship['ID Shipper']==i][['order_creation_datetime',section]], on='order_creation_datetime', how='left')[section].fillna('None')
        traces.append(go.Bar(
            x=dateline['period'],
            y=data_y,
            name=index_name,
            text=data_y,
            textposition = 'auto'
        ))
    return {
        'data': traces,
        'layout': {
            'autosize': True,
            'showlegend': True,
            'legend': {'font':{'size':'9'}},
            'xaxis': {'showgrid': True,'showline': True, 'showticklabels':True, 'title':'Periode','ticks':'outside'},
            'yaxis': {'showgrid': True,'showline': True, 'zeroline':False, 'showticklabels':True, 'title':y_title},
            'title': 'Shipper Squad Shipment Detail'
        }
    }

#create line chart
def admin_bikin_grafik_squad(squad_name, datasqu, dateline, section):
    # change title for y axis
    if section=="Volume":
        y_title = "Total Shipment"
    else:
        y_title = "Biaya Pengiriman"
    traces = []
    for i in squad_name :
        index_name = datasqu[datasqu['ID Squad']==i]['Nama Squad'].iloc[0]
        data_y = pd.merge(dateline['order_creation_datetime'], datasqu[datasqu['ID Squad']==i][['order_creation_datetime',section]], on='order_creation_datetime', how='left')[section].fillna('None')
        traces.append(go.Bar(
            x=dateline['period'],
            y=data_y,
            name=index_name,
            text=data_y,
            textposition = 'auto'
        ))
    return {
        'data': traces,
        'layout': {
            'autosize': True,
            'showlegend': True,
            'legend': {'font':{'size':'9'}},
            'xaxis': {'showgrid': True,'showline': True, 'showticklabels':True, 'title':'Periode','ticks':'outside'},
            'yaxis': {'showgrid': True,'showline': True, 'zeroline':False, 'showticklabels':True, 'title':y_title},
            'title': 'Squad Shipment Detail'
        }
    }

#create pie chart
def admin_bikin_pie_shipper(jumlah_paket):
    return {
        'data': [go.Pie(
            labels = ['Completed', 'On Hold', 'Cancelled', 'Pending', 'RTS'],
            hole=.3,
            values = jumlah_paket,
            text = jumlah_paket,
            textposition = 'auto'
        )],
        'layout': {
            'autosize': True,
            'showlegend': True,
            'legend': {'font':{'size':'9'}},
            'title': 'Shipper Order'
        }
    }

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_admin', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                children=[
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="row",
                            children=[
                                html.Div('Silakan tentukan periode dan cakupan waktu yang ingin Anda ketahui.'),
                                html.Div([
                                dcc.DatePickerRange(
                                    id='admin_pilih-tanggal',
                                    min_date_allowed=datetime.date(2013, 1, 1),
                                    max_date_allowed=datetime.date.today(),
                                    start_date=None,
                                    end_date=None
                                    )
                                ], className="six columns", style={'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto'}
                                ),
                                html.Div([dcc.Dropdown(
                                    id='admin_pilih-scope',
                                    options=[
                                        {'label': 'per Jam', 'value': 'H'},
                                        {'label': 'Harian', 'value': 'D'},
                                        {'label': 'Mingguan', 'value': 'W'},
                                        {'label': 'Bulanan', 'value': 'M'},
                                        {'label': 'Kuartal', 'value': 'Q'},
                                        {'label': 'Tahunan', 'value': 'Y'}
                                    ],
                                    value='W')
                                    ], className="six columns", style={'padding-top':'6.5px'}
                                ),
                                html.Div("Pilih status paket terkini :", className="twelve columns", style={'margin-top':'6.5px'}),
                                html.Div([dcc.Dropdown(
                                    id='admin_pilih-granular-status',
                                    options=[{'label':granularstatus[i], 'value':granularstatus[i]} for i in range(len(granularstatus))],
                                    multi=True,
                                    value=granularstatus),
                                    ], className="twelve columns"
                                )
                            ]
                        ),

                        html.Hr(),

                        html.Div(id='admin_salam-perolehan'),
                        html.Div(className="bingkaiteks",
                            children=[
                                html.Div(id='admin_uang'),
                                html.Div(id='admin_paket', style={'line-height':'19px'})
                            ],
                            style={
                            'text-align': 'center'
                        }),

                        html.Div(
                            id="admin_konten",
                            # style={'display':'none'},
                            children=[
                                html.Div(
                                    className="twelve columns",
                                    children=[
                                        html.Br(),
                                        html.Div("Di bawah ini adalah grafik perolehan Squad secara keseluruhan dalam periode. Grafik bar menunjukkan perolehan volume dan grafik garis menunjukkan biaya pengiriman."),
                                        dcc.Graph(id='admin_grafik-summary-week')
                                    ]
                                ),
                                html.Div(
                                    className="twelve columns",
                                    children=[
                                        html.Div(children=("Di bawah adalah tabel perolehan shipment per Squad. Untuk menampilkan grafik dan tabel rinci shipment per Squad, silakan pilih dari daftar squad pada tabel di bawah dengan menandai kotak di tabel kolom paling kiri.", html.A("Klik di sini untuk mengunduh data tabel berikut.", download="squad-table.xlsx", id='link_download-squad-data', target="_blank"))),
                                        dt.DataTable(
                                            rows=[{}],
                                            columns=['Nama Squad','Volume','Biaya Pengiriman'],
                                            filterable=True,
                                            row_selectable=True,
                                            sortable=True,
                                            selected_row_indices=[],
                                            id='admin_squad-table')
                                    ]
                                ),
                                html.Div(
                                    className="twelve columns",
                                    style={'display':'none'},
                                    children=[
                                        dt.DataTable(
                                            rows=[{}],
                                            id='admin_save_df'),
                                        dt.DataTable(
                                            rows=[{}],
                                            id='admin_save_df_2'),
                                        dt.DataTable(
                                            rows=[{}],
                                            id='admin_save_df_3'),
                                        dt.DataTable(
                                            rows=[{}],
                                            id='admin_save_df_4'),
                                        dt.DataTable(
                                            rows=[{}],
                                            id='admin_save_df_5')
                                    ]
                                ),
                                html.Div(
                                    id="admin_squad-shipper-section",
                                    children=[
                                    html.Div(
                                        className="twelve columns",
                                        id="admin_shipper-section",
                                        children=[
                                            html.Div("Di bawah ini adalah grafik shipment dari squad yang dipilih. Silakan pilih metrik yang ingin Anda ketahui.", style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                            dcc.Dropdown(
                                                id='admin_pilih-section-squad',
                                                options=[
                                                    {'label': 'Volume', 'value': 'Volume'},
                                                    {'label': 'Biaya Pengiriman', 'value': 'Biaya Pengiriman'}
                                                ],
                                                value='Volume'
                                            ),
                                            dcc.Graph(id='admin_chart-squad')
                                        ]
                                    ),
                                    html.Div(
                                        className="twelve columns",
                                        id="admin_squad-section",
                                        children=[
                                            html.Div(children=("Di bawah adalah tabel perolehan order per shipper dari squad yang dipilih pada tabel di atas. Anda juga dapat memilih shipper untuk mengetahui lebih rinci perkembangan shipper tersebut. Adapun angka Hit SLA berikut adalah persentase hit/miss paket di tanggal terpilih, terlepas dari paket yang hit/miss blank yang ada di kolom Blank SLA.", html.A("Klik di sini untuk mengunduh data tabel berikut.", download="shipper-table.xlsx", id='link_download-shipper-data', target="_blank"))),
                                            dt.DataTable(
                                                rows=[{}],
                                                columns=['Nama Shipper','Volume','Hit SLA','Blank SLA','Biaya Pengiriman'],
                                                filterable=True,
                                                row_selectable=True,
                                                sortable=True,
                                                selected_row_indices=[],
                                                id='admin_shipper-progress-table')
                                        ]
                                    )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className="twelve columns",
                            id="admin_shipper-section",
                            children=[
                                html.Div("Di bawah ini adalah grafik shipment untuk shipper yang dipilih. Silakan pilih metrik yang ingin Anda ketahui.", style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                dcc.Dropdown(
                                    id='admin_pilih-section-shipper',
                                    options=[
                                        {'label': 'Volume', 'value': 'Volume'},
                                        {'label': 'Biaya Pengiriman', 'value': 'Biaya Pengiriman'}
                                    ],
                                    value='Volume'
                                ),
                                dcc.Graph(id='admin_chart-shipper'),
                                html.Div("Sedangkan berikut adalah diagram lingkaran dari persentase status-status paket dari shipper yang dipilih.", style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                dcc.Graph(id='admin_pie-chart-shipper')
                            ]
                        ),

                        html.Div(
                            id = "admin_no-content",
                            children=[
                                html.Img(src='assets/maapin.webp', style={'display': 'block', 'max-width':'30%', 'margin-left': 'auto',
                                    'margin-right': 'auto', 'margin-top':'35px'},
                                    className='row'),
                                html.Div("Mohon maaf, tidak ada perkembangan pada periode tersebut.", style={'text-align': 'center','font-weight':'bold'})
                                ]
                        ),

                        html.Br(),
                        html.Div(children=("Data yang ditampilkan pada dashboard ini (termasuk status terkini paket shipper) ditentukan berdasarkan data yang terakhir kali diupdate di database. ", html.A('Anda bisa klik tautan ini untuk memperbaharui data.', href="/admin-upload-data", target="_blank")), style={'padding-top':'12px', 'margin-bottom':'7px'}),
                        html.Hr(),
                        html.Div(
                            children=[
                                html.Button(
                                    children='Perlihatkan Keseluruhan Ninja Squad',
                                    n_clicks=0,
                                    type='submit',
                                    id='admin_squad-list-button',
                                    className="twelve columns",
                                    style={'background-color':'#138d75', 'color':'white', 'margin-top':'10px'}
                                )
                            ], className="row"
                        ),
                        html.Div(
                            id = "admin_list-squad-section",
                            children=[
                            html.Div(children=("Berikut adalah daftar squad yang terdaftar di Ninja. Jumlah shipper ditulis dalam format shipper aktif dibanding seluruh shipper squad tersebut. Angka 1 dalam kolom Squadash berarti squad tersebut sudah terdaftar dalam Squadash. Karena dashboard masih manual, Anda bisa klik pada ", html.A('link berikut', href='/admin-database-squad', target="_blank"), " untuk menambahkan squad baru. Sedangkan untuk mendaftarkan squad pada SquaDash, anda bisa klik pada ", html.A("link berikut", href="/admin-add-squad", target="_blank"), "."), style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                dt.DataTable(
                                    rows=[{}],
                                    columns=["ID Squad","Nama Squad","Waktu Terdaftar","Jumlah Shipper","Akun SquaDash"],
                                    filterable=True,
                                    sortable=True,
                                    id='admin_list-squad-table')
                                ]
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    children='Perlihatkan Keseluruhan Shipper Squad',
                                    n_clicks=0,
                                    type='submit',
                                    id='admin_shipper-list-button',
                                    className="twelve columns",
                                    style={'background-color':'#138d75', 'color':'white', 'margin-top':'30px'}
                                )
                            ], className="row"
                        ),
                        html.Div(
                            id = "admin_list-shipper-section",
                            children=[
                            html.Div(children=("Berikut adalah daftar shipper squad yang terdaftar di Ninja. Karena dashboard masih manual, Anda bisa klik pada ", html.A('link berikut', href='/admin-database-shipper', target="_blank"), " untuk menambahkan shipper baru."), style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                dt.DataTable(
                                    rows=[{}],
                                    columns=['Nama Shipper','ID Sales','Waktu Terdaftar','Shipment Pertama','Shipment Terkini'],
                                    filterable=True,
                                    sortable=True,
                                    id='admin_list-shipper-table')
                                ]
                        )
                    ]
                )
                ]
            )
        ]
    ),
])


# Create callbacks
@app.callback(Output('admin_list-shipper-section', 'style'),
              [Input('admin_shipper-list-button', 'n_clicks')])
def tunjukkan_tabel(klik_showtable):
    if klik_showtable%2 == 1:
        return {'display':'block'}
    else:
        return {'display':'none'}

@app.callback(Output('admin_list-squad-section', 'style'),
              [Input('admin_squad-list-button', 'n_clicks')])
def tunjukkan_tabel(klik_showtable):
    if klik_showtable%2 == 1:
        return {'display':'block'}
    else:
        return {'display':'none'}

# Callback agar pilihan tanggal dinamis di VPS
@app.callback([Output('admin_pilih-tanggal','start_date'),
                Output('admin_pilih-tanggal', 'end_date')],
              [Input('url_admin', 'pathname')])
def dinamiskan_tanggal(input):
    return datetime.date.today()-datetime.timedelta(days=14), datetime.date.today()

@app.callback(
    [Output('admin_chart-shipper', 'figure'),
    Output('admin_pie-chart-shipper', 'figure'),
    Output('admin_shipper-section', 'style')],
    [Input('admin_shipper-progress-table', 'rows'),
    Input('admin_save_df_4', 'rows'),
    Input('admin_save_df_5', 'rows'),
    Input('admin_save_df_2', 'rows'),
    Input('admin_shipper-progress-table', 'selected_row_indices'),
        Input('admin_pilih-section-shipper', 'value')])
def gambarkan_chart_shipper(shipper_rows, shipper_chart_temp, pie_shipper_chart, dateline_temp, selected_row_indices, section):
    shipper_aux = pd.DataFrame(shipper_rows)
    dataship = pd.DataFrame(shipper_chart_temp)
    dateline = pd.DataFrame(dateline_temp)
    pie_shippers = pd.DataFrame(pie_shipper_chart)
    try:
        dataship.order_creation_datetime = pd.to_datetime(dataship.order_creation_datetime)
        dateline.order_creation_datetime = pd.to_datetime(dateline.order_creation_datetime)
    except:
        pass
    # Select shipper
    if len(selected_row_indices) == 0:
        return admin_bikin_grafik_shipper([], dataship, dateline, section), admin_bikin_pie_shipper([]), {'display':'none'}
    else:
        # ['Completed', 'On Hold', 'Cancelled', 'Pending', 'RTS'],
        temp_df = list(shipper_aux.iloc[selected_row_indices, :]['ID Shipper'])
        pie_shippers = pie_shippers[pie_shippers.shipper_id.isin(temp_df)][["rts_flag","granular_status","tracking_id"]]
        pie_shippers_nonrts = pie_shippers[pie_shippers.rts_flag=="Non RTS"]
        jumlah_paket_rts = pie_shippers.sum()['tracking_id']-pie_shippers_nonrts.sum()['tracking_id']
        jumlah_paket_completed = pie_shippers[pie_shippers.granular_status=="Completed"].sum()["tracking_id"]
        jumlah_paket_cancelled = pie_shippers[pie_shippers.granular_status=="Cancelled"].sum()["tracking_id"]
        jumlah_paket_onhold = pie_shippers[pie_shippers.granular_status=="On Hold"].sum()["tracking_id"]
        jumlah_paket_pending = pie_shippers[~pie_shippers.granular_status.isin(["Completed","On Hold","Cancelled"])].sum()['tracking_id']
        jumlah_paket = [jumlah_paket_completed, jumlah_paket_onhold, jumlah_paket_cancelled, jumlah_paket_pending, jumlah_paket_rts]
        return admin_bikin_grafik_shipper(temp_df, dataship, dateline, section), admin_bikin_pie_shipper(jumlah_paket), {'display':'block'}

@app.callback(
    [Output('admin_shipper-progress-table','rows'),
    Output('admin_chart-squad', 'figure'),
    Output('admin_squad-shipper-section', 'style'),
    Output('link_download-shipper-data','href')],
    [Input('admin_squad-table', 'rows'),
    Input('admin_save_df', 'rows'),
    Input('admin_save_df_2', 'rows'),
    Input('admin_save_df_3', 'rows'),
    Input('admin_squad-table', 'selected_row_indices'),
        Input('admin_pilih-section-squad', 'value')])
def gambarkan_chart_squad(squad_rows, squad_temp, dateline_temp, shippers_temp, selected_row_indices, section):
    squad_aux = pd.DataFrame(squad_rows)
    datasqu = pd.DataFrame(squad_temp)
    dateline = pd.DataFrame(dateline_temp)
    shippersquad = pd.DataFrame(shippers_temp)
    try:
        dataship.order_creation_datetime = pd.to_datetime(dataship.order_creation_datetime)
        dateline.order_creation_datetime = pd.to_datetime(dateline.order_creation_datetime)
    except:
        pass
    # Select squad
    if len(selected_row_indices) == 0:
        return [], admin_bikin_grafik_squad([], datasqu, dateline, section), {'display':'none'}, ''
    else:
        temp_df = list(squad_aux.iloc[selected_row_indices, :]['ID Squad'])
        shippersquad = shippersquad[shippersquad['ID Squad'].isin(temp_df)]
        strIO = io.BytesIO()
        writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
        shippersquad.to_excel(writer, sheet_name="result", index=False)
        worksheet = writer.sheets["result"]
        workbook = writer.book
        for j, width in enumerate(get_col_widths(shippersquad)):
            worksheet.set_column(j-1, j-1, width)
        writer.save()
        strIO.seek(0)

        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file = base64.b64encode(strIO.read()).decode("utf-8")
        excel = f'data:{media_type};base64,{file}'
        shippersquad['Biaya Pengiriman'] = shippersquad['Biaya Pengiriman'].apply(format_currency, currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
        shippersquad = shippersquad.to_dict('records')
        return shippersquad, admin_bikin_grafik_squad(temp_df, datasqu, dateline, section), {'display':'block'}, excel

@app.callback(
    [Output('admin_squad-table', 'rows'),
    Output('admin_save_df','rows'),
    Output('admin_save_df_2','rows'),
    Output('admin_save_df_3','rows'),
    Output('admin_save_df_4','rows'),
    Output('admin_save_df_5','rows'),
    Output('admin_list-shipper-table','rows'),
    Output('admin_list-squad-table','rows'),
    Output('admin_uang','children'),
    Output('admin_paket','children'),
    Output('admin_grafik-summary-week','figure'),
    Output('admin_salam-perolehan','children'),
    Output('admin_konten','style'),
    Output('admin_no-content','style'),
    Output('link_download-squad-data','href')],
    [Input('admin_pilih-tanggal', 'start_date'),
    Input('admin_pilih-tanggal', 'end_date'),
    Input('admin_pilih-scope', 'value'),
    Input('admin_pilih-granular-status', 'value')])
def bentuk_data(waktumin,waktumax,aggregation,granular):
    data = pd.read_pickle("./data/data.pkl").set_index('order_creation_datetime')[['sales_person','sales_person_name','granular_status','rts_flag','shipper_id','shipper_name','tracking_id','delivery_fee','hit/miss']]
    # Indexing min and max shipment of each shipper
    minmax_ship = data.reset_index()[['shipper_id','order_creation_datetime']].groupby('shipper_id').agg({'order_creation_datetime':[np.min, np.max]}).reset_index()
    minmax_ship.columns = ['shipper_id','First Shipment','Last Shipment']
    minmax_ship['First Shipment'] = minmax_ship['First Shipment'].dt.date
    minmax_ship['Last Shipment'] = minmax_ship['Last Shipment'].dt.date
    # Filter data by date chosen
    mapsshp = data[waktumin:waktumax]
    # Giving percentage of SLA hit/miss
    pivot_sla = pd.pivot_table(mapsshp[mapsshp.rts_flag!="RTS"], columns="hit/miss", index="shipper_id", aggfunc={'tracking_id':'count'}).reset_index().fillna(0)
    # Filter by granular status and format specific column
    mapsshp = mapsshp[mapsshp.granular_status.isin(granular)]
    # Importing shipper data
    all_shippers = pd.read_pickle("./data/shippers.pkl")[['shipper_id','shipper_name','squad_code','create_dashboard']]
    all_shippers.create_dashboard = all_shippers.create_dashboard.dt.date
    # Merging shipper data with min max of each shipment
    all_shippers = pd.merge(all_shippers,minmax_ship,on='shipper_id',how='left')
    # Providing shipper counted per squad for further use
    mapping_shippersquad = all_shippers.groupby('squad_code').count()[["shipper_id","First Shipment"]].reset_index()
    mapping_shippersquad['shipper_count'] = mapping_shippersquad['First Shipment'].map(str) + "/" + mapping_shippersquad.shipper_id.map(str)
    all_squad = pd.read_pickle("./data/squad.pkl")[['code','name','created_at']]
    all_squad.created_at = all_squad.created_at.dt.date
    all_squad["squad_code"] = all_squad.code.str.split("-").str[-1]
    squadash_squad = um.list_users()
    all_squad["squadash"] = np.where(all_squad.squad_code.isin(squadash_squad), 1, 0)
    all_squad = pd.merge(all_squad,mapping_shippersquad[["squad_code","shipper_count"]],on="squad_code",how="left").fillna("0/0")
    # Convert the squad dataframe into dictionary
    all_squad.columns = ["ID Squad Complete","Nama Squad","Waktu Terdaftar","ID Squad","Akun SquaDash","Jumlah Shipper"]
    all_squad = all_squad.to_dict('records')
    # Convert the shipper dataframe into dictionary
    all_shippers.columns = ['Shipper ID','Nama Shipper','ID Sales','Waktu Terdaftar','Shipment Pertama','Shipment Terkini']
    all_shippers = all_shippers.to_dict('records')
    # Data for table grouped by squad
    squad_data = mapsshp.groupby(['sales_person','sales_person_name']).agg({'tracking_id':'count','delivery_fee':'sum'}).reset_index()
    # Data for barchart (summary of all shipper)
    bardata_squad = mapsshp.resample(aggregation).agg({'tracking_id':'count','delivery_fee':'sum'}).reset_index()
    bardata_squad.columns = ['order_creation_datetime','Volume','Biaya Pengiriman']
    # Count the data summary
    hitung_paket_admin = str(int(squad_data.sum()['tracking_id']))
    # hitung_uang_squad = format_currency(int(summary_mapsshp['commission_squad']), currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
    hitung_uang_admin = format_currency(int(mapsshp['delivery_fee'].sum()), currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
    # Get the text period of datetime
    tanggalmin = datetime.datetime.strptime(waktumin, '%Y-%m-%d').strftime('%d %B %Y')
    tanggalmax = datetime.datetime.strptime(waktumax, '%Y-%m-%d').strftime('%d %B %Y')
    # Check whether dataframe is empty or not to display the formatted page
    if len(squad_data) != 0:
        # Editing SLA Percentage only if there is data
        pivot_sla['percentage'] = pivot_sla['tracking_id']['hit']/(pivot_sla['tracking_id']['hit']+pivot_sla['tracking_id']['miss'])
        pivot_sla['percentage'] = pivot_sla['percentage'].map(lambda x: '{:.2%}'.format(x))
        pivot_sla['blanks'] = pivot_sla['tracking_id']['']/(pivot_sla['tracking_id'].sum(axis=1))
        pivot_sla['blanks'] = pivot_sla['blanks'].map(lambda x: '{:.2%}'.format(x))
        pivot_sla = pivot_sla.drop('tracking_id', axis=1, level=0)
        # Temporary data for squad chart
        data_temp = mapsshp.groupby(['sales_person','sales_person_name']).resample(aggregation).agg({'tracking_id':'count','delivery_fee':'sum'}).reset_index()
        data_temp.columns = ['ID Squad','Nama Squad','order_creation_datetime','Volume','Biaya Pengiriman']
        data_temp = data_temp.to_dict('records')
        # Temporary data for shipper table
        shipper_temp = mapsshp.groupby(['shipper_id','shipper_name','sales_person']).agg({'tracking_id':'count','delivery_fee':'sum'}).reset_index()
        shipper_temp = pd.merge(shipper_temp, pivot_sla, on="shipper_id", how="left")
        shipper_temp.columns = ['ID Shipper','Nama Shipper','ID Squad','Volume','Biaya Pengiriman','Hit SLA', "Blank SLA"]
        shipper_temp = shipper_temp.to_dict('records')
        # Temporary data for shipper charset
        ship_chart_temp = mapsshp.groupby(['shipper_id','shipper_name','sales_person']).resample(aggregation).agg({'tracking_id':'count','delivery_fee':'sum'}).reset_index()
        ship_chart_temp.columns = ['ID Shipper','Nama Shipper','ID Squad','order_creation_datetime','Volume','Biaya Pengiriman']
        ship_chart_temp = ship_chart_temp.to_dict('records')
        # Data for piechart package status
        pie_shipper = mapsshp.groupby(['shipper_id','shipper_name','rts_flag','granular_status']).count()[['tracking_id']].reset_index()
        pie_shipper = pie_shipper.to_dict('records')
        # Making dateline for displaying x axis on chart
        dateline = pd.date_range(start=waktumin, end=waktumax)
        dateline = pd.DataFrame([]*len(dateline),index=dateline).resample(aggregation).count().reset_index()
        dateline.columns = ['order_creation_datetime']
        if aggregation == "W":
            dateline['period'] = dateline['order_creation_datetime'].apply(lambda x: 'W'+ x.strftime('%W') + " " + x.strftime('%y'))
        elif aggregation == "M":
            dateline['period'] = dateline['order_creation_datetime'].apply(lambda x: x.strftime('%b') + " " + x.strftime('%y'))
        elif aggregation == "Q":
            dateline['period'] = dateline['order_creation_datetime'].apply(lambda x: "Q"+str(x.quarter)+" "+str(x.year))
        elif aggregation == "Y":
            dateline['period'] = dateline['order_creation_datetime'].apply(lambda x: str(x.year))
        else:
            dateline['period'] = dateline['order_creation_datetime']
        dateline_temp = dateline.to_dict('records')
        strIO = io.BytesIO()
        writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
        squad_data.to_excel(writer, sheet_name="result", index=False)
        worksheet = writer.sheets["result"]
        workbook  = writer.book
        for j, width in enumerate(get_col_widths(squad_data)):
            worksheet.set_column(j-1, j-1, width)
        writer.save()
        strIO.seek(0)

        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file = base64.b64encode(strIO.read()).decode("utf-8")
        excel = f'data:{media_type};base64,{file}'
        # Format the currency
        squad_data['delivery_fee'] = squad_data['delivery_fee'].apply(format_currency, currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
        squad_data.columns = ['ID Squad','Nama Squad','Volume','Biaya Pengiriman']
        squad_rows = squad_data.to_dict('records')
        return (squad_rows, data_temp, dateline_temp, shipper_temp, ship_chart_temp, pie_shipper, all_shippers, all_squad, html.H5('Total biaya pengiriman yang terhitung : '+hitung_uang_admin), html.P("dari "+hitung_paket_admin+" paket."),
            admin_bikin_barchart(bardata_squad, dateline, aggregation), html.P('Ini adalah hasil perolehan Ninja Squad dari '+tanggalmin+' hingga '+tanggalmax+' (data terakhir diperbarui pada '+data.index.max().date().strftime('%d %B %Y')+' dan angka berikut hanya sebagai perkiraan):'),
            {'display':'block'},{'display':'none'}, excel)
    else:
        return ([],[],[],[],[],[], all_shippers, all_squad, html.H5('Total biaya pengiriman yang terhitung : '+hitung_uang_admin), html.P("dari "+hitung_paket_admin+" paket."),
            [], html.P('Ini adalah hasil perolehan Ninja Squad dari '+tanggalmin+' hingga '+tanggalmax+' (data terakhir diperbarui pada '+data.index.max().date().strftime('%d %B %Y')+' dan angka berikut hanya sebagai perkiraan):'),
            {'display':'none'},{'display':'block'}, '/')
