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

persentase_komisi = 15/100


# databaru['coach'] = temp.apply(lambda x:x[2] if len(x)==4 else "coach-itself")

# Quote database
quote = pd.read_excel("./data/quotesquad.xlsx", header=None)

#create summary Bar
def squad_bikin_barchart(dff, dateline, aggregation):
    data_x = dateline['period']
    data_y_vol = pd.merge(dateline['order_creation_datetime'], dff, how='left')['Volume'].fillna('None')
    data_y_money = pd.merge(dateline['order_creation_datetime'], dff, how='left')['Komisi Pengiriman'].fillna('None')
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
                name='Komisi',
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
            'yaxis2': {'showgrid': True,'showline': True, 'zeroline':False, 'showticklabels':True, 'title':'Komisi Pengiriman', 'overlaying':'y', 'side':'right'},
            'title': 'Grafik Perkembangan Anda'
        }
    }

#create line chart
def squad_bikin_grafik_shipper(shipper_name, dataship, dateline, section):
    # change title for y axis
    if section=="Volume":
        y_title = "Total Shipment"
    else:
        y_title = "Komisi Pengiriman"
    traces = []
    for i in shipper_name :
        data_y = pd.merge(dateline['order_creation_datetime'], dataship[dataship['Nama Shipper']==i][['order_creation_datetime',section]], on='order_creation_datetime', how='left')[section].fillna('None')
        traces.append(go.Bar(
            x=dateline['period'],
            y=data_y,
            name=i,
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
            'title': 'Shipper Shipment Detail'
        }
    }

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_squad', refresh=True),
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
                                    id='squad_pilih-tanggal',
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
                                    id='squad_pilih-scope',
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
                                )
                            ]
                        ),

                        html.Hr(),

                        html.Div(id='squad_salam-perolehan'),
                        html.Div(className="bingkaiteks",
                            children=[
                                html.Div(id='squad_uang'),
                                html.Div(id='squad_paket', style={'line-height':'19px'})
                            ],
                            style={
                            'text-align': 'center'
                        }),

                        html.Div(
                            id="squad_konten",
                            # style={'display':'none'},
                            children=[
                                html.Div(
                                    className="twelve columns",
                                    children=[
                                        html.Br(),
                                        html.Div("Di bawah ini adalah grafik perolehan Anda secara keseluruhan dalam periode. Grafik bar menunjukkan perolehan volume dan grafik garis menunjukkan perolehan komisi."),
                                        dcc.Graph(id='squad_grafik-summary-week')
                                    ]
                                ),
                                html.Div(
                                    className="twelve columns",
                                    children=[
                                        html.Div("Di bawah adalah tabel perolehan shipment per shipper di bawah Anda. Untuk menampilkan grafik order per shipment, silakan pilih dari daftar shipper Anda pada tabel di bawah dengan menandai kotak di tabel kolom paling kiri."),
                                        dt.DataTable(
                                            rows=[{}],
                                            columns=['Nama Shipper','Volume','Komisi Pengiriman'],
                                            filterable=True,
                                            row_selectable=True,
                                            sortable=True,
                                            selected_row_indices=[],
                                            id='squad_shipper-table')
                                    ]
                                ),
                                html.Div(
                                    className="twelve columns",
                                    style={'display':'none'},
                                    children=[
                                        dt.DataTable(
                                            rows=[{}],
                                            id='save_df'),
                                        dt.DataTable(
                                            rows=[{}],
                                            id='save_df_2')
                                    ]
                                ),
                                html.Div(
                                    className="twelve columns",
                                    id="squad_shipper-section",
                                    children=[
                                        html.Div("Di bawah ini adalah grafik shipment untuk shipper yang dipilih. Silakan pilih metrik yang ingin Anda ketahui.", style={'margin-top':'12px', 'margin-bottom':'7px'}),
                                        dcc.Dropdown(
                                            id='squad_pilih-section-shipper',
                                            options=[
                                                {'label': 'Volume', 'value': 'Volume'},
                                                {'label': 'Komisi Pengiriman', 'value': 'Komisi Pengiriman'}
                                            ],
                                            value='Volume'
                                        ),
                                        dcc.Graph(id='squad_chart-shipper')
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id = "squad_no-content",
                            children=[
                                html.Img(src='assets/maapin.webp', style={'display': 'block', 'max-width':'30%', 'margin-left': 'auto',
                                    'margin-right': 'auto', 'margin-top':'35px'},
                                    className='row'),
                                html.Div("Mohon maaf, Anda belum memiliki perkembangan pada periode tersebut.", style={'text-align': 'center','font-weight':'bold'})
                                ]
                        ),
                        html.Br(),
                        html.Hr(),
                        html.Div(
                            children=[
                                html.Button(
                                    children='Perlihatkan Keseluruhan Shipper Saya',
                                    n_clicks=0,
                                    type='submit',
                                    id='squad_shipper-list-button',
                                    className="twelve columns",
                                    style={'background-color':'#138d75', 'color':'white', 'margin-top':'30px'}
                                )
                            ], className="row"
                        ),
                        html.Div(
                            id = "squad_list-shipper-section",
                            children=[
                                dt.DataTable(
                                    rows=[{}],
                                    columns=['Nama Shipper','Waktu Terdaftar','Shipment Pertama','Shipment Terkini'],
                                    filterable=True,
                                    sortable=True,
                                    id='squad_list-shipper-table')
                                ]
                        )
                    ]
                ),

                html.Hr(),
                html.Div(id='squad_salam-penutup'),
                html.Div(
                    className="bingkaisalams",
                    children=[
                        html.Div(className="row",
                            children=[
                                html.Img(
                                    src='assets/idea.webp',
                                    className="two columns",
                                    style={'max-width':'35%', 'margin-right':'14px'}
                                ),
                                html.Div(id="squad_kutipan")
                            ]
                        ),
                        html.P('', style={'margin-bottom' : '8px'}),
                        html.Div(
                            children=[
                                html.Button(
                                    children='Kembali ke Beranda',
                                    n_clicks=0,
                                    type='submit',
                                    id='squad_back-button',
                                    className="twelve columns",
                                    style={'background-color':'#138d75', 'color':'white'}
                                )
                            ], className="row"
                        ),
                    ]
                )
                ]
            )
        ]
    ),
])


# Create callbacks
@app.callback(Output('url_squad', 'pathname'),
              [Input('squad_back-button', 'n_clicks')])
def balik_ke_beranda(klik_backtohome):
    if klik_backtohome > 0:
        return '/'

@app.callback(Output('squad_list-shipper-section', 'style'),
              [Input('squad_shipper-list-button', 'n_clicks')])
def tunjukkan_tabel(klik_showtable):
    if klik_showtable%2 == 1:
        return {'display':'block'}
    else:
        return {'display':'none'}

# Callback agar pilihan tanggal dinamis di VPS
@app.callback([Output('squad_pilih-tanggal','start_date'),
                Output('squad_pilih-tanggal', 'end_date'),
                Output('squad_kutipan', 'children')],
              [Input('url_squad', 'pathname')])
def dinamiskan_tanggal(input):
    kutipan = quote.iloc[randint(0,len(quote)-1),:]
    return datetime.date.today()-datetime.timedelta(days=14), datetime.date.today(), html.Div(
        children=[
            html.Div(kutipan[0],
            style={
                'font-style' : 'italic'
            }),
            html.Div("- "+kutipan[1],
            style={
                'font-weight' : 'bold'
            })
        ], className="ten columns"
    )

@app.callback(
    [Output('squad_chart-shipper', 'figure'),
    Output('squad_shipper-section', 'style')],
    [Input('squad_shipper-table', 'rows'),
    Input('save_df', 'rows'),
    Input('save_df_2', 'rows'),
    Input('squad_shipper-table', 'selected_row_indices'),
    Input('squad_pilih-section-shipper', 'value')])
def gambarkan_chart_shipper(rows, rows_temp, dateline_temp, selected_row_indices, section):
    aux = pd.DataFrame(rows)
    dataship = pd.DataFrame(rows_temp)
    dateline = pd.DataFrame(dateline_temp)
    try:
        dataship.order_creation_datetime = pd.to_datetime(dataship.order_creation_datetime)
        dateline.order_creation_datetime = pd.to_datetime(dateline.order_creation_datetime)
    except:
        pass
    # Select shipper
    if len(selected_row_indices) == 0:
        temp_df = []
        return squad_bikin_grafik_shipper([], dataship, dateline, section), {'display':'none'}
    else:
        temp_df = list(aux.iloc[selected_row_indices, :]['Nama Shipper'])
        return squad_bikin_grafik_shipper(temp_df, dataship, dateline, section), {'display':'block'}

@app.callback(
    [Output('squad_shipper-table', 'rows'),
    Output('save_df','rows'),
    Output('save_df_2','rows'),
    Output('squad_list-shipper-table','rows'),
    Output('squad_uang','children'),
    Output('squad_paket','children'),
    Output('squad_grafik-summary-week','figure'),
    Output('squad_salam-perolehan','children'),
    Output('squad_salam-penutup','children'),
    Output('squad_konten','style'),
    Output('squad_no-content','style')],
    [Input('squad_pilih-tanggal', 'start_date'),
    Input('squad_pilih-tanggal', 'end_date'),
    Input('squad_pilih-scope', 'value')])
def bentuk_data(waktumin,waktumax,aggregation):
    squad = current_user.username
    data = pd.read_pickle("./data/data.pkl").set_index('order_creation_datetime')[['sales_person','granular_status','rts_flag','shipper_id','shipper_name','tracking_id','delivery_fee']]
    # Indexing min and max shipment of each shipper
    compl_ship = data.reset_index()[['shipper_id','order_creation_datetime']].groupby('shipper_id').agg({'order_creation_datetime':[np.min, np.max]}).reset_index()
    compl_ship.columns = ['shipper_id','First Shipment','Last Shipment']
    compl_ship['First Shipment'] = compl_ship['First Shipment'].dt.date
    compl_ship['Last Shipment'] = compl_ship['Last Shipment'].dt.date
    # Importing list of shipper
    shippers = pd.read_pickle("./data/shippers.pkl")[['squad_code','squad_name','shipper_name','shipper_id','create_dashboard']]
    shippers.create_dashboard = shippers.create_dashboard.dt.date
    data = data[(data.granular_status=='Completed') & (data.rts_flag!="RTS")]
    # Filter the database for the specific active squad
    if squad == "RYO2019":
        mapsshp = data[data.sales_person.str.split('-').str[-1]=="JUN33"][waktumin:waktumax]
        table_compl_ship = shippers[shippers.squad_code=="JUN33"][["shipper_id","shipper_name","create_dashboard"]]
    else:
        mapsshp = data[data.sales_person.str.split('-').str[-1]==squad][waktumin:waktumax]
        table_compl_ship = shippers[shippers.squad_code==squad][["shipper_id","shipper_name","create_dashboard"]]
    # Format the specific rows
    mapsshp['commission_squad'] = mapsshp['delivery_fee']*persentase_komisi
    # Merging All Shipper Data
    table_compl_ship = pd.merge(table_compl_ship,compl_ship,on='shipper_id',how='left')
    table_compl_ship.columns = ['Shipper ID','Nama Shipper','Waktu Terdaftar','Shipment Pertama','Shipment Terkini']
    table_compl_ship = table_compl_ship.to_dict('records')
    # Data for table grouped per shipper
    shipper_data = mapsshp.groupby(['shipper_id','shipper_name']).agg({'tracking_id':'count','commission_squad':'sum'}).reset_index().drop('shipper_id', axis=1)
    # Data for barchart (summary of all shipper)
    bardata_squad = mapsshp.resample(aggregation).agg({'tracking_id':'count','commission_squad':'sum'}).reset_index()
    bardata_squad.columns = ['order_creation_datetime','Volume','Komisi Pengiriman']
    # Count the data summary
    summary_mapsshp = shipper_data.sum()
    hitung_paket_squad = str(int(summary_mapsshp['tracking_id']))
    hitung_uang_squad = format_currency(int(summary_mapsshp['commission_squad']), currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
    hitung_omset_squad = format_currency(int(mapsshp['delivery_fee'].sum()), currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
    # Get the text period of datetime
    tanggalmin = datetime.datetime.strptime(waktumin, '%Y-%m-%d').strftime('%d %B %Y')
    tanggalmax = datetime.datetime.strptime(waktumax, '%Y-%m-%d').strftime('%d %B %Y')
    # Check whether dataframe is empty or not to display the formatted page
    if len(shipper_data) != 0:
        # Temporary data for shipper chart
        data_temp = mapsshp.groupby(['shipper_id','shipper_name']).resample(aggregation).agg({'tracking_id':'count','commission_squad':'sum'}).reset_index().drop('shipper_id', axis=1)
        data_temp.columns = ['Nama Shipper','order_creation_datetime','Volume','Komisi Pengiriman']
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
        # Format the currency
        shipper_data['commission_squad'] = shipper_data['commission_squad'].apply(format_currency, currency='IDR', format=u'Rp #,##0.00', locale='id_ID', currency_digits=False)
        shipper_data.columns = ['Nama Shipper','Volume','Komisi Pengiriman']
        rows = shipper_data.to_dict('records')
        data_temp = data_temp.to_dict('records')
        return (rows, data_temp, dateline_temp, table_compl_ship, html.H5('Uang yang Anda peroleh : '+hitung_uang_squad), html.P("dengan omset "+hitung_omset_squad+" dari "+hitung_paket_squad+" paket."),
            squad_bikin_barchart(bardata_squad, dateline, aggregation), html.P('Ini adalah hasil perolehan Anda dari '+tanggalmin+' hingga '+tanggalmax+' (data terakhir diperbarui pada '+data.index.max().date().strftime('%d %B %Y')+' dan angka berikut hanya sebagai perkiraan):'),
            html.H5("Keep up the good work! Siap untuk menjelajah lebih jauh?", className="row", style={'text-align':'center'}),
            {'display':'block'},{'display':'none'})
    else:
        return ([],[],[], table_compl_ship, html.H5('Uang yang Anda peroleh : '+hitung_uang_squad), html.P("dengan omset "+hitung_omset_squad+" dari "+hitung_paket_squad+" paket."),
            [], html.P('Ini adalah hasil perolehan Anda dari '+tanggalmin+' hingga '+tanggalmax+' (data terakhir diperbarui pada '+data.index.max().date().strftime('%d %B %Y')+' dan angka berikut hanya sebagai perkiraan):'),
            html.H5("Tetap semangat! Ryo akan selalu membantu apabila ada kesulitan.", className="row", style={'text-align':'center'}),
            {'display':'none'},{'display':'block'})
