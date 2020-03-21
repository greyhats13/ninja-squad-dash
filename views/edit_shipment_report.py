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
import datetime
from six.moves.urllib.parse import quote
import csv
from fpdf import FPDF
import seaborn as sns
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
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

def editdata(temp, holiday, waktumax):
    for i in range(len(temp)):
        if temp.granular_status.iloc[i] != "Cancelled" :
            if pd.isnull(temp.inbound_cutoff.iloc[i]) == True :
                pass
            else :
                if pd.isnull(temp.first_attempt_at.iloc[i]) == True :
                    temp.delivery_duration.iloc[i] = np.busday_count(temp.inbound_cutoff.iloc[i], waktumax, weekmask='1111110', holidays=list(holiday.date))

    temp['over_sla'] = temp.delivery_duration - temp.service_days.astype(float)
    temp_rts = temp[temp.rts_flag=="RTS"]
    tempcom = temp[~temp.granular_status.isin(['Pending Pickup','Cancelled'])]
    tempcom = tempcom[tempcom.rts_flag!="RTS"]
    oversla = tempcom.groupby('over_sla').count()['tracking_id'].to_frame().reset_index()
    return tempcom, temp_rts, oversla

def get_col_widths(dataframe):
    # Menentukan panjang maksimum dari kolom index
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Menggabungkan maksimum dari panjang kolom dan panjang data dari kolom tersebut
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_edit_shipment', refresh=True),
                html.H3('Download Squad Shipment Data', style={'text-align':'center'}),
                dcc.RadioItems(
                id='admin_pilih_jenis_file',
                options=[
                {'label': 'PDF', 'value': 'PDF'},
                {'label': 'Excel', 'value': 'Excel'}
                ],
                value='PDF', labelStyle={'display': 'inline-block'}
                ),
                html.Div(
                id = "download_data_excel_section",
                children=
                [html.Hr(),
                html.Div(children=[
                html.Div(children="Pilih Squad: "),
                dcc.Dropdown(
                    id='admin_choose_squad',
                    value='NSQ-XXX0-XXX0-INS268', className="twelve columns")
                    ], className="row", style={'padding-top':'3px'}
                ),
                html.Div(children=[
                html.Div(children="Pilih Shipper: "),
                dcc.Dropdown(
                    id='admin_choose_shipper', value=0, className="twelve columns")
                    ], className="row", style={'padding-top':'3px'}
                ),
                html.Div(children=[
                dcc.Checklist(
                id='checklist_daterange',
                options=[{'label': 'Enable Date Picker Range', 'value': 'ena'}],
                values=[],
                labelStyle={'display': 'inline-block', 'padding-bottom':'6px'}
                )
                ]),
                html.Div(id='datepicker_report_section',children=[
                html.Div(children='Pilih Tanggal:', className='three columns'),
                dcc.DatePickerRange(
                id='admin_download_pilih-tanggal',
                min_date_allowed=datetime.date(2013, 1, 1),
                max_date_allowed=datetime.date.today(),
                start_date=None,
                end_date=None)], className='row'
                ),
                html.Button(
                        id='download_excel_data_button',
                        n_clicks=0,
                        type='submit',
                        className="row",
                        children='Process Data to Excel',
                        style={'background-color':'#1d6f42',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '12px'}
                    ),
                html.Div(id='excel_hasil_download', style={'text-align': 'center'})
                ]
                ),
                html.Div(
                id = "download_data_pdf_section",
                children=
                [html.Hr(),
                html.Div(children=[
                html.Div(children="Pilih Shipper: "),
                dcc.Dropdown(
                    id='admin_pdf_choose_shipper', value=199855, className="twelve columns")
                    ], className="row", style={'padding-top':'3px'}
                ),
                html.Div(id='datepicker_lastweek_section',children=[
                html.Div(children='Pilih Range Awal:', className='three columns'),
                dcc.DatePickerRange(
                id='admin_tgl_lastweek',
                min_date_allowed=datetime.date(2013, 1, 1),
                max_date_allowed=datetime.date.today(),
                start_date=None,
                end_date=None)], className='row'
                ),
                html.Div(id='datepicker_thisweek_section',children=[
                html.Div(children='Pilih Range Akhir:', className='three columns'),
                dcc.DatePickerRange(
                id='admin_tgl_thisweek',
                min_date_allowed=datetime.date(2013, 1, 1),
                max_date_allowed=datetime.date.today(),
                start_date=None,
                end_date=None)], className='row'
                ),
                html.Button(
                        id='download_pdf_data_button',
                        n_clicks=0,
                        type='submit',
                        className="row",
                        children='Process Data to PDF',
                        style={'background-color':'#c0392b',
                        'color':'white',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-top': '12px'}
                    ),
                html.Div(id='pdf_hasil_download', style={'text-align': 'center'})
                ]
                )
            ]
        )
    ]
)

@app.callback(
    [Output('excel_hasil_download', 'children'),
    Output('url_edit_shipment', 'href')],
    [Input('download_excel_data_button', 'n_clicks'),
    Input('download_pdf_data_button', 'n_clicks')],
    [State('admin_choose_squad','value'),
    State('admin_choose_shipper','value'),
    State('admin_pdf_choose_shipper','value'),
    State('admin_download_pilih-tanggal','start_date'),
    State('admin_download_pilih-tanggal', 'end_date'),
    State('admin_tgl_lastweek','start_date'),
    State('admin_tgl_lastweek', 'end_date'),
    State('admin_tgl_thisweek','start_date'),
    State('admin_tgl_thisweek', 'end_date'),
    State('checklist_daterange', 'values'),
    State('admin_pilih_jenis_file', 'value')])
def pull_data(klik_download_excel, klik_download_pdf, squad_id, shipper_id, pdf_shipper_id, tanggal_awal, tanggal_akhir, pdf_last_awal, pdf_last_akhir, pdf_this_awal, pdf_this_akhir, trigger, jenis_file):
    data_wh = pd.read_pickle('./data/data.pkl').set_index('order_creation_datetime')
    holiday = pd.read_pickle('./data/holiday.pkl')
    if jenis_file=="Excel":
        if klik_download_excel > 0:
            if squad_id != 0:
                data_wh = data_wh[data_wh.sales_person == squad_id]
                squad_name = data_wh.sales_person.str.split('-').str[-1].iloc[0]
            else:
                squad_name = "All-Squad"
                pass
            if shipper_id != 0:
                data_wh = data_wh[data_wh.shipper_id == shipper_id]
                shipper_name = str(data_wh.shipper_id.iloc[0])
            else:
                shipper_name = "All-Shipper"
                pass
            if len(trigger) == 1:
                data_wh = data_wh[tanggal_awal:tanggal_akhir]
                tanggal = tanggal_awal+"_"+tanggal_akhir
            else:
                tanggal = "All-Date"
                pass
            data_wh = data_wh.reset_index()
            data_wh = data_wh.drop(['first_att_name','first_att_email','first_att_contact','first_att_address1','first_att_address2','first_att_postcode','delivery_fee_origin','first_attempt_date'], axis=1)
            data_wh = data_wh.reindex(columns=['order_creation_datetime', 'tracking_id', 'shipper_id',
           'shipper_name', 'sales_person', 'sales_person_name', 'kecamatan', 'kabupaten',
           'delivery_address', 'rts_flag', 'service_type', 'granular_status',
           'to_postcode', 'order_comments', 'first_inbound_datetime',
           'inbound_cutoff', 'from_billing_zone', 'to_billing_zone',
           'first_inb_hub', 'dest_hub', 'dest_region', 'submitted_weight',
           'actual_weight', 'parcel_size', 'width', 'height', 'length',
           'pod_datetime', 'pod_recipient_name', 'pod_photo_url',
           'pod_signature_url', 'first_attempt_at', 'first_fail_reason',
           'last_attempt_at', 'last_fail_reason', 'delivery_fee', 'service_days', 'delivery_duration', 'hit/miss'])
            strIO = io.BytesIO()
            writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
            data_wh.to_excel(writer, sheet_name="result", index=False)
            worksheet = writer.sheets["result"]
            workbook  = writer.book
            tebal = workbook.add_format({'bold': True})
            for j, width in enumerate(get_col_widths(data_wh)):
                worksheet.set_column(j-1, j-1, width)
            worksheet.set_column('I:I', 20)
            worksheet.set_column('AC:AC', 20)
            worksheet.set_column('AD:AD', 20)
            worksheet.set_column('AE:AE', 20)
            writer.save()
            strIO.seek(0)

            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file = base64.b64encode(strIO.read()).decode("utf-8")
            excel = f'data:{media_type};base64,{file}'

            return (('Excel untuk squad '+squad_name+' dan shipper '+shipper_name+' sudah selesai dibuat gannnn.', html.A('Klik di sini buat download.', download=squad_name+"_"+shipper_name+"_"+tanggal+".xlsx", href=excel, target="_blank")), None)
        else :
            return '', None
    elif jenis_file=="PDF":
        if klik_download_pdf > 0:
            temp = data_wh[pdf_this_awal:pdf_this_akhir].reset_index()
            temp = temp[temp.shipper_id == pdf_shipper_id]
            last_temp = data_wh[pdf_last_awal:pdf_last_akhir].reset_index()
            last_temp = last_temp[last_temp.shipper_id == pdf_shipper_id]
            pdf = FPDF()
            pdf.add_page()
            pdf.ln(10)
            pdf.image('assets/logo_pdf.webp', x=10, y=18, w=40)
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(220,50,50)
            pdf.cell(191, 10, txt="Report", align = 'R')

            pdf.ln(23)

            timemin = datetime.datetime.strptime(pdf_this_awal,'%Y-%m-%d').strftime('%d %b %Y')
            timemax = datetime.datetime.strptime(pdf_this_akhir,'%Y-%m-%d').strftime('%d %b %Y')

            pdf.set_font("Arial", size=9)
            pdf.set_text_color(0,0,0)
            pdf.cell(110, 5, txt="PT. ANDIARTA MUZIZAT")
            pdf.cell(30, 5, "Period  :", 0, align='R')
            pdf.cell(50, 5, "{}".format(timemin+" - "+timemax), 1, 1, 'L', 0)

            pdf.cell(110, 5, "Jl. Gatot Subroto No.Kav. 71-73, RT.8/RW.8")
            pdf.cell(30, 5, "Report Date  :", 0, align='R')
            pdf.cell(50, 5, "{}".format(datetime.datetime.today().strftime('%d %b %Y')), 1, 1, 'L', 0)

            pdf.cell(110, 5, "Menteng Dalam, Kec. Tebet, Kota Jakarta Selatan",0,1)

            pdf.cell(20, 5, txt="DKI Jakarta Indonesia")

            pdf.ln(25)

            pdf.set_font('Arial', 'B', size=11)
            pdf.cell(140, 5, "Shipment Report to", 0, 1, 'L', 0)
            pdf.ln(1)
            pdf.set_font("Arial", size=9)
            pdf.cell(30, 5, "Name", 0, align='L')
            pdf.cell(3, 5, ": ", 0, align='L')
            try :
                nama_shipper = temp.shipper_name.iloc[0]
                pdf.cell(157, 5, "{}".format(nama_shipper), 0, 1, 'L', 0)
                pdf.cell(30, 5, "Address", 0, align='L')
                pdf.cell(3, 5, ": ", 0, align='L')
                # pdf.multi_cell(157, 5, "{}".format(shipper_list[shipper_list.shipper_id==temp.shipper_id.iloc[0]].liaison_address.iloc[0]), 0, 1, 'L', 0)
                pdf.multi_cell(157, 5, "{}".format("sss"), 0, 1, 'L', 0)

                pdf.ln(17)

                pdf.set_font("Arial", size=9)
                pdf.set_text_color(0,0,0)
                pdf.multi_cell(190, 5, "        Shipment "+nama_shipper+" untuk periode minggu sebelumnya ("+timemin+" hingga "+timemax+") sejumlah "+str(len(temp))+" paket, dengan paket yang sudah berstatus \"Completed\" sejauh ini sejumlah "+str(len(temp[temp.granular_status=="Completed"]))+" dari keseluruhan paket. Adapun rincian lebih lengkap status terkini paket pengiriman Anda adalah sebagai berikut", 0, 1, 'L', 0)

                pdf.ln(3)

                pdf.set_font("Arial", 'B', 9)
                pdf.set_draw_color(220,50,50)
                pdf.set_fill_color(220,50,50)
                pdf.set_text_color(255,255,255)

                pdf.cell(40, 5, "RTS Flag", 0, 0, 'C', 1)
                pdf.cell(90, 5, "Granular Status", 0, 0, 'C', 1)
                pdf.cell(60, 5, "Banyaknya Paket", 0, 1, 'C', 1)

                stats = temp.groupby(['rts_flag','granular_status']).count()[['tracking_id']]

                if 'Non RTS' in stats.index.levels[0].values :
                    nonrts = stats.loc['Non RTS']
                    pdf.set_text_color(0,0,0)
                    for j in range(len(nonrts)):
                    	if j%2 == 0:
                    		pdf.set_fill_color(240,240,240)
                    		pdf.set_font("Arial", 'B', size=9)
                    		if j == 0:
                    			pdf.cell(40, 5, "Non RTS", 0, 0,'C',1)
                    		else:
                    			pdf.cell(40, 5, "", 0, 0,'C',1)
                    		pdf.cell(90, 5, nonrts.index[j], 0, 0,'C',1)
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(60, 5, str(nonrts.tracking_id[j]), 0, 1,'C',1)
                    	elif j%2 == 1:
                    		pdf.set_font("Arial", 'B', size=9)
                    		pdf.cell(40, 5, "", 0, 0,align='C')
                    		pdf.cell(90, 5, nonrts.index[j], 0, 0,align='C')
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(60, 5, str(nonrts.tracking_id[j]), 0, 1,align='C')
                    pos_y_bar = pdf.get_y()
                    pdf.set_fill_color(250,177,160)
                    pdf.set_draw_color(20,20,20)
                    pdf.line(10, pos_y_bar, 200, pos_y_bar)
                    pdf.set_font("Arial", 'B', size=9)
                    pdf.cell(40, 5, "", 0, 0,'C',1)
                    pdf.cell(90, 5, "Grand Total (Non RTS)", 0, 0,'C',1)
                    pdf.set_font("Arial", size=9)
                    pdf.cell(60, 5, str(nonrts.tracking_id.sum()), 0, 1,'C',1)
                    pdf.line(10, pos_y_bar+5, 200, pos_y_bar+5)

                if 'RTS' in stats.index.levels[0].values :
                    if 'Non RTS' not in stats.index.levels[0].values :
                    	nonrts = []
                    rts = stats.loc['RTS']
                    pdf.set_text_color(0,0,0)
                    for j in range(len(rts)):
                    	if (len(nonrts)+1+j)%2 == 0:
                    		pdf.set_fill_color(240,240,240)
                    		pdf.set_font("Arial", 'B', size=9)
                    		if j == 0:
                    			pdf.cell(40, 5, "RTS", 0, 0,'C',1)
                    		else:
                    			pdf.cell(40, 5, "", 0, 0,'C',1)
                    		pdf.cell(90, 5, rts.index[j], 0, 0,'C',1)
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(60, 5, str(rts.tracking_id[j]), 0, 1,'C',1)
                    	elif (len(nonrts)+1+j)%2 == 1:
                    		pdf.set_font("Arial", 'B', size=9)
                    		if j == 0:
                    			pdf.cell(40, 5, "RTS", 0, 0,'C')
                    		else:
                    			pdf.cell(40, 5, "", 0, 0,'C')
                    		pdf.cell(90, 5, rts.index[j], 0, 0,align='C')
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(60, 5, str(rts.tracking_id[j]), 0, 1,align='C')
                    pos_y_bar = pdf.get_y()
                    pdf.set_fill_color(250,177,160)
                    pdf.set_draw_color(20,20,20)
                    pdf.line(10, pos_y_bar, 200, pos_y_bar)
                    pdf.set_font("Arial", 'B', size=9)
                    pdf.cell(40, 5, "", 0, 0,'C',1)
                    pdf.cell(90, 5, "Grand Total (RTS)", 0, 0,'C',1)
                    pdf.set_font("Arial", size=9)
                    pdf.cell(60, 5, str(rts.tracking_id.sum()), 0, 1,'C',1)
                    pdf.line(10, pos_y_bar+5, 200, pos_y_bar+5)

                    pdf.set_fill_color(255,255,255)
                    pdf.set_font("Arial", 'B', size=9)
                    pdf.cell(40, 5, "", 0, 0,'C',1)
                    pdf.cell(90, 5, "Grand Total", 0, 0,'C',1)
                    pdf.set_font("Arial", size=9)
                    pdf.cell(60, 5, str(stats.tracking_id.sum()), 0, 1,'C',1)
                    # pdf.line(10, pos_y_bar+5, 200, pos_y_bar+5)

                # Get data grouped by SLA
                tempcom, temp_rts, oversla = editdata(temp,holiday,pdf_this_akhir)
                last_tempcom, last_temp_rts, last_oversla = editdata(last_temp,holiday,pdf_last_akhir)

                count_sla = oversla[oversla.over_sla>0]['tracking_id'].sum()
                if len(tempcom)!=0:
                    percent_sla = count_sla/len(tempcom)*100
                else:
                    percent_sla = 0
                if len(last_tempcom) != 0:
                    last_count_sla = last_oversla[last_oversla.over_sla>0]['tracking_id'].sum()
                    last_percent_sla = last_count_sla/len(last_tempcom)*100
                    if percent_sla > last_percent_sla :
                    	status_sla = "mengalami kenaikan"
                    elif percent_sla < last_percent_sla :
                    	status_sla = "mengalami penurunan"
                    else :
                    	status_sla = "tidak mengalami perubahan"
                else :
                    pass

                pdf.ln(2.5)
                if len(last_tempcom) != 0:
                    pdf.multi_cell(190, 5, "          Adapun paket yang terindikasi mengalami Over SLA pada minggu lalu ada sebanyak "+str(count_sla)+" paket (sekitar "+"{:.2f}%".format(percent_sla)+" dari total paket yang dikirimkan), yang mana "+status_sla+" dari minggu sebelumnya dengan sekitar "+"{:.2f}%".format(last_percent_sla)+" dari total paket yang dikirimkan. Untuk penjelasan lebih lengkap mengenai status terkini paket Anda, dapat dilihat pada appendiks di lembar berikutnya.", 0, 1, 'L', 0)
                else:
                    pdf.multi_cell(190, 5, "          Adapun paket yang terindikasi mengalami Over SLA pada minggu lalu ada sebanyak "+str(count_sla)+" paket (sekitar "+"{:.2f}%".format(percent_sla)+" dari total paket yang dikirimkan). Untuk penjelasan lebih lengkap mengenai status terkini paket Anda, dapat dilihat pada appendiks di lembar berikutnya.", 0, 1, 'L', 0)
                pdf.ln(5)
                pdf.cell(190, 5, "", 0, ln=1)

                pdf.ln(2)

                pdf.set_xy(10,265)
                pdf.set_font('Arial', size=7)
                pdf.cell(190, 4, "If you have any question about this invoice, please contact our Client Relation",align = 'C',ln=1)
                pdf.set_font('Arial', 'BI', 7)
                pdf.cell(190, 4, "Thank you for your Business!",align = 'C',ln=1)

                pdf.add_page()
                pdf.ln(5)
                pdf.set_font('Arial', 'B', size=11)
                pdf.cell(140, 5, "Monitoring Status Paket", 0, 1, 'L', 0)
                pdf.ln(1)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Terdapat 6 status paket normal :", 0, 1, 'L', 0)

                pdf.image('assets/Picture1.webp', x=15, y=28, w=10)
                pdf.set_xy(27.5,28)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Pending Pickup", 0, 1, 'L', 0)
                pdf.set_xy(27.5,33)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket berada di seller belum di pickup oleh NinjaXpress atau seller belum drop out ke NinjaXpress", 0, 1, 'L', 0)

                pdf.image('assets/Picture1.webp', x=15, y=40, w=10)
                pdf.set_xy(27.5,40)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Pending Pickup at Distribution Point", 0, 1, 'L', 0)
                pdf.set_xy(27.5,45)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket berada di Mitra dan belum di di pick up oleh Ninja Rider atau Ninja Driver.", 0, 1, 'L', 0)

                pdf.image('assets/Picture2.webp', x=15, y=52, w=10)
                pdf.set_xy(27.5,52)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "En-route at Sorting Hub", 0, 1, 'L', 0)
                pdf.set_xy(27.5,57)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket sudah dipick up oleh rider dan dalam perjalanan menuju station.", 0, 1, 'L', 0)

                pdf.image('assets/Picture3.webp', x=15, y=64, w=10)
                pdf.set_xy(27.5,64)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Arrived at Sorting Hub", 0, 1, 'L', 0)
                pdf.set_xy(27.5,69)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket sudah tiba di station dan diproses lebih lanjut.", 0, 1, 'L', 0)

                pdf.image('assets/Picture2.webp', x=15, y=76, w=10)
                pdf.set_xy(27.5,76)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "On Vehicle for Delivery", 0, 1, 'L', 0)
                pdf.set_xy(27.5,81)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Proses pengantaran paket ke alamat penerima.", 0, 1, 'L', 0)

                pdf.image('assets/Picture4.webp', x=15, y=88, w=10)
                pdf.set_xy(27.5,88)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Completed", 0, 1, 'L', 0)
                pdf.set_xy(27.5,93)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket sudah sampai ke tangan penerima.", 0, 1, 'L', 0)

                pdf.ln(3)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Terdapat 3 status paket tidak normal :", 0, 1, 'L', 0)

                pdf.image('assets/Picture2.webp', x=15, y=108, w=10)
                pdf.set_xy(27.5,108)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Return to Sender (RTS)", 0, 1, 'L', 0)
                pdf.set_xy(27.5,113)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket dikirim kepada penerima maksimal 2 kali namun penerima tidak ada, maka paket dikembalikan kepada pengirim.", 0, 1, 'L', 0)

                pdf.image('assets/Picture3.webp', x=15, y=120, w=10)
                pdf.set_xy(27.5,120)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "On Hold", 0, 1, 'L', 0)
                pdf.set_xy(27.5,125)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket sudah diproses oleh ninja namun terdapat kendala.", 0, 1, 'L', 0)

                pdf.image('assets/Picture4.webp', x=15, y=132, w=10)
                pdf.set_xy(27.5,132)
                pdf.set_font('Arial', 'B', size=9)
                pdf.cell(190, 5, "Cancelled", 0, 1, 'L', 0)
                pdf.set_xy(27.5,137)
                pdf.set_font('Arial', size=9)
                pdf.cell(190, 5, "Paket dibatalkan melalui permintaan pengirim atau penerima.", 0, 1, 'L', 0)
                pos_x_bar = pdf.get_x()
                pos_y_bar = pdf.get_y()

                try:
                    sns.set(rc={'figure.figsize':(13.7,4.27)})
                    print("cek2")
                    pdf.set_xy(pos_x_bar,pos_y_bar+1)
                    pdf.ln(7)
                    pdf.set_font('Arial', 'B', size=11)
                    pdf.cell(140, 5, "Rincian Status Terkini Paket", 0, 1, 'L', 0)
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()
                    bar = sns.barplot(x="over_sla", y="tracking_id", data=oversla)
                    pdf.ln(1)
                    pdf.set_font('Arial', size=9)
                    if len(last_tempcom) != 0:
                    	pdf.multi_cell(190, 5, "Dari paket yang Anda kirimkan pada minggu ini dan sebelumnya, berikut adalah representasi paket yang dikelompokkan berdasarkan SLA dengan durasi pengiriman dan dibandingkan per minggunya. Nilai negatif mengindikasikan paket tersebut sampai di penerima sebelum SLA.", 0, 1, 'L', 0)
                    else:
                    	pdf.multi_cell(190, 5, "Dari paket yang Anda kirimkan pada minggu ini, berikut adalah representasi paket yang dikelompokkan berdasarkan SLA dengan durasi pengiriman dan dibandingkan per minggunya. Nilai negatif mengindikasikan paket tersebut sampai di penerima sebelum SLA.", 0, 1, 'L', 0)
                    for index, row in oversla.iterrows():
                    	bar.text(row.name, row.tracking_id, int(row.tracking_id), color='#202020', ha='center')
                    bar.set_title(nama_shipper+' Parcels (This Week)')
                    plt.xlabel('Durasi Pengiriman - Service Days SLA')
                    plt.ylabel('Banyaknya Paket')
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()
                    pdf.set_font('Arial', 'B', size=11)
                    plt.savefig('assets/temp/nonrtssla2.webp', bbox_inches='tight')
                    plt.close()
                    pdf.image('assets/temp/nonrtssla2.webp', x=32.5, y=pos_y_bar+2, w=142.5)
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()+52
                    try:
                    	bar = sns.barplot(x="over_sla", y="tracking_id", data=last_oversla)
                    	for index, row in last_oversla.iterrows():
                    		bar.text(row.name, row.tracking_id, int(row.tracking_id), color='#202020', ha='center')
                    	bar.set_title(nama_shipper+' Parcels (Last Week)')
                    	plt.xlabel('Durasi Pengiriman - Service Days SLA')
                    	plt.ylabel('Banyaknya Paket')
                    	pdf.set_font('Arial', 'B', size=11)
                    	pdf.set_xy(pos_x_bar,pos_y_bar+1)
                    	pdf.cell(190, 5, "VS", 0, 1, 'C', 0)
                    	plt.savefig('assets/temp/nonrtssla.webp', bbox_inches='tight')
                    	plt.close()
                    	pdf.image('assets/temp/nonrtssla.webp', x=32.5, y=pos_y_bar+5, w=142.5)
                    	pos_x_bar = pdf.get_x()
                    	pos_y_bar = pdf.get_y()+52
                    except:
                    	pass
                except:
                	pass
                try:
                    sns.set(rc={'figure.figsize':(7.7,4.27)})
                    label = ['Completed', 'On Hold', 'Cancelled', 'Pending']
                    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
                    explode = (0.05,0.05,0.05,0.05)
                    sizes = np.array([len(temp[temp.granular_status=="Completed"]), len(temp[temp.granular_status=="On Hold"]), len(temp[temp.granular_status=="Cancelled"]), len(temp[~temp.granular_status.isin(["Completed","On Hold","Cancelled"])])])
                    fig = Figure(tight_layout=True)
                    ax = fig.add_subplot(1,1,1)
                    patches,texts = ax.pie(sizes, colors=colors, startangle=90, explode = explode)#draw circle
                    percent = 100*sizes/sizes.sum()
                    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(label, percent)]
                    sort_legend = True
                    if sort_legend:
                    	patches, labels, dummy =  zip(*sorted(zip(patches, labels, sizes),key=lambda x: x[2],reverse=True))
                    ax.legend(patches, labels, loc='best', bbox_to_anchor=(-0.1, 1.), fontsize=14)
                    centre_circle = plt.Circle((0,0),0.70,fc='white')
                    ax.add_artist(centre_circle)# Equal aspect ratio ensures that pie is drawn as a circle
                    ax.axis('equal')
                    ax.set_title('Parcels Status (This Week)')
                    FigureCanvasAgg(fig).print_png('assets/temp/percentage2.webp', dpi=300)
                    pdf.set_xy(10,pos_y_bar+3.5)
                    pdf.set_font('Arial', size=9)
                    if len(last_tempcom)!=0:
                    	pdf.multi_cell(190, 5, "Berikut adalah prosentase status paket minggu lalu dibandingkan dengan minggu ini.", 0, 1, 'L', 0)
                    else:
                    	pdf.multi_cell(190, 5, "Berikut adalah prosentase status paket Anda minggu ini.", 0, 1, 'L', 0)
                    pos_x_bar_temp = pdf.get_x()
                    pos_y_bar_temp = pdf.get_y()
                    if len(last_tempcom)!=0:
                    	# pdf.set_xy(10,pos_y_bar+5)
                    	pdf.image('assets/temp/percentage2.webp', x=110, w=90)
                    	sizes = np.array([len(last_temp[last_temp.granular_status=="Completed"]), len(last_temp[last_temp.granular_status=="On Hold"]), len(last_temp[last_temp.granular_status=="Cancelled"]), len(last_temp[~last_temp.granular_status.isin(["Completed","On Hold","Cancelled"])])])
                    	fig = Figure(tight_layout=True)
                    	ax = fig.add_subplot(1,1,1)
                    	patches,texts = ax.pie(sizes, colors=colors, startangle=90, explode = explode)#draw circle
                    	percent = 100*sizes/sizes.sum()
                    	labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(label, percent)]
                    	sort_legend = True
                    	if sort_legend:
                    		patches, labels, dummy =  zip(*sorted(zip(patches, labels, sizes),key=lambda x: x[2],reverse=True))
                    	ax.legend(patches, labels, loc='best', bbox_to_anchor=(-0.1, 1.), fontsize=14)
                    	centre_circle = plt.Circle((0,0),0.70,fc='white')
                    	ax.add_artist(centre_circle)# Equal aspect ratio ensures that pie is drawn as a circle
                    	ax.axis('equal')
                    	ax.set_title('Parcels Status (Last Week)')
                    	FigureCanvasAgg(fig).print_jpeg('assets/temp/percentage.jpeg', dpi=300)
                    	pdf.set_xy(10,pos_y_bar_temp+1)
                    	pdf.image('assets/temp/percentage.webp', w=90)
                    	pdf.set_xy(10,pos_y_bar_temp+17.5)
                    	pdf.set_font('Arial', 'B', size=11)
                    	pdf.cell(190, 5, "VS", 0, 1, 'C', 0)
                    	pos_x_bar = pdf.get_x()
                    	pos_y_bar = pdf.get_y()+27.5
                    else:
                    	pdf.image('assets/temp/percentage2.webp', x=55, y=pos_y_bar_temp+1, w=90)
                    	pos_x_bar = pdf.get_x()
                    	pos_y_bar = pdf.get_y()+50
                except:
                	pass
                firstreason = tempcom[tempcom.over_sla>0].groupby(['first_fail_reason']).count()[['tracking_id']]
                if len(firstreason) != 0:
                    pdf.set_xy(pos_x_bar,pos_y_bar)
                    pdf.set_font("Arial", size=9)
                    pdf.multi_cell(190, 5, "Beberapa alasan yang tercantum untuk paket yang Over SLA atas gagalnya pengiriman pertama adalah sebagai berikut", 0, 1, 'L', 0)
                    pdf.set_font("Arial", 'B', 9)
                    pdf.set_draw_color(220,50,50)
                    pdf.set_fill_color(220,50,50)
                    pdf.set_text_color(255,255,255)

                    pdf.cell(140, 5, "Fail Reason", 0, 0, 'C', 1)
                    pdf.cell(50, 5, "Banyaknya Paket", 0, 1, 'C', 1)

                    for j in range(len(firstreason)):
                    	if j%2 == 0:
                    		pdf.set_fill_color(240,240,240)
                    		pdf.set_text_color(0,0,0)
                    		pdf.set_font("Arial", 'B', size=9)
                    		pdf.cell(140, 5, firstreason.index[j], 0, 0,'C',1)
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(50, 5, str(firstreason.tracking_id[j]), 0, 1,'C',1)
                    	elif j%2 == 1:
                    		pdf.set_font("Arial", 'B', size=9)
                    		pdf.cell(140, 5, firstreason.index[j], 0, 0,align='C')
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(50, 5, str(firstreason.tracking_id[j]), 0, 1,align='C')
                    	pos_x_bar = pdf.get_x()
                    	pos_y_bar = pdf.get_y()
                    pdf.set_fill_color(255,255,255)
                    pdf.set_draw_color(20,20,20)
                    pdf.line(10, pos_y_bar, 200, pos_y_bar)
                    pdf.set_font("Arial", 'B', size=9)
                    pdf.cell(140, 5, "Grand Total", 0, 0,'C',1)
                    pdf.set_font("Arial", size=9)
                    pdf.cell(50, 5, str(firstreason.tracking_id.sum()), 0, 1,'C',1)
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()
                else:
                    pass
                temp_rts = temp[temp.rts_flag=="RTS"]
                rts_reason = temp_rts.groupby('first_fail_reason').count()[['tracking_id']]
                if len(rts_reason) != 0:
                    pdf.set_xy(pos_x_bar,pos_y_bar+3)
                    pdf.set_font("Arial", size=9)
                    pdf.multi_cell(190, 5, "Beberapa alasan yang tercantum untuk paket RTS atas gagalnya pengiriman pertama adalah sebagai berikut", 0, 1, 'L', 0)
                    pdf.set_font("Arial", 'B', 9)
                    pdf.set_draw_color(220,50,50)
                    pdf.set_fill_color(220,50,50)
                    pdf.set_text_color(255,255,255)

                    pdf.cell(140, 5, "RTS Reason", 0, 0, 'C', 1)
                    pdf.cell(50, 5, "Banyaknya Paket", 0, 1, 'C', 1)

                    for j in range(len(rts_reason)):
                    	if j%2 == 0:
                    		pdf.set_fill_color(240,240,240)
                    		pdf.set_text_color(0,0,0)
                    		pdf.set_font("Arial", 'B', size=9)
                    		pdf.cell(140, 5, rts_reason.index[j], 0, 0,'C',1)
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(50, 5, str(rts_reason.tracking_id[j]), 0, 1,'C',1)
                    	elif j%2 == 1:
                    		pdf.set_font("Arial", 'B', size=9)
                    		pdf.cell(140, 5, rts_reason.index[j], 0, 0,align='C')
                    		pdf.set_font("Arial", size=9)
                    		pdf.cell(50, 5, str(rts_reason.tracking_id[j]), 0, 1,align='C')
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()
                    pdf.set_fill_color(255,255,255)
                    pdf.set_draw_color(20,20,20)
                    pdf.line(10, pos_y_bar, 200, pos_y_bar)
                    pdf.set_font("Arial", 'B', size=9)
                    pdf.cell(140, 5, "Grand Total", 0, 0,'C',1)
                    pdf.set_font("Arial", size=9)
                    pdf.cell(50, 5, str(rts_reason.tracking_id.sum()), 0, 1,'C',1)
                    pos_x_bar = pdf.get_x()
                    pos_y_bar = pdf.get_y()
                else:
                    pass

                path = os.getcwd()
                result_path = os.getcwd() + '/assets/pdf_temp/'
                if not os.path.exists(result_path):
                    os.makedirs(result_path)
                pdf.output(result_path + str(int(temp.shipper_id.iloc[0])) + " " + "Report {}".format(temp.shipper_name.iloc[0]) + ".pdf")
                media_type = 'application/pdf'
                with open(result_path + str(int(temp.shipper_id.iloc[0])) + " " + "Report {}".format(temp.shipper_name.iloc[0]) + ".pdf", "rb") as pdf_file:
                    file = base64.b64encode(pdf_file.read()).decode("utf-8")
                excel = f'data:{media_type};base64,{file}'
                os.remove(result_path + str(int(temp.shipper_id.iloc[0])) + " " + "Report {}".format(temp.shipper_name.iloc[0]) + ".pdf")
                return ('', None)
            except Exception as ex:
                return ('', None)
        else:
            return '', None

@app.callback([Output('admin_download_pilih-tanggal','start_date'),
                Output('admin_download_pilih-tanggal', 'end_date'),
                Output('admin_tgl_lastweek','start_date'),
                Output('admin_tgl_lastweek', 'end_date'),
                Output('admin_tgl_thisweek','start_date'),
                Output('admin_tgl_thisweek', 'end_date'),
                Output('admin_choose_squad','options'),
                Output('admin_pdf_choose_shipper','options')],
              [Input('url_edit_shipment', 'pathname')])
def pilih_squad(input):
    data_wh = pd.read_pickle('./data/data.pkl')
    data_shipper = data_wh[['shipper_id','shipper_name']].drop_duplicates('shipper_id').sort_values(by='shipper_name').reset_index(drop=True)
    data_wh = data_wh[['sales_person','sales_person_name']].drop_duplicates('sales_person').sort_values(by='sales_person_name').reset_index(drop=True)
    return (datetime.date.today()-datetime.timedelta(days=14), datetime.date.today(),
    # datetime.date.today()-datetime.timedelta(days=14), datetime.date.today()-datetime.timedelta(days=8),
    # datetime.date.today()-datetime.timedelta(days=7), datetime.date.today()-datetime.timedelta(days=1),
    '2019-09-01', '2019-09-07', '2019-09-08', '2019-09-15',
    [{'label': '---ALL SQUAD---', 'value': 0}]+[{'label':data_wh.sales_person_name[i]+' ('+data_wh.sales_person.str.split('-').str[-1][i]+')', 'value':data_wh.sales_person[i]} for i in range(len(data_wh))],
    [{'label':data_shipper.shipper_name[i]+ ' ('+str(data_shipper.shipper_id[i])+')', 'value':data_shipper.shipper_id[i]} for i in range(len(data_shipper))])

@app.callback(Output('admin_choose_shipper','options'),
              [Input('admin_choose_squad', 'value')])
def pilih_shipper(input):
    data_shipper = pd.read_pickle('./data/data.pkl')
    if input!=0:
        data_shipper = data_shipper[data_shipper.sales_person==input][['shipper_id','shipper_name']].drop_duplicates('shipper_id').sort_values(by='shipper_name').reset_index(drop=True)
    else:
        data_shipper = data_shipper[['shipper_id','shipper_name']].drop_duplicates('shipper_id').sort_values(by='shipper_name').reset_index(drop=True)
    return [{'label': '---ALL SHIPPER---', 'value': 0}]+[{'label':data_shipper.shipper_name[i]+ ' ('+str(data_shipper.shipper_id[i])+')', 'value':data_shipper.shipper_id[i]} for i in range(len(data_shipper))]

@app.callback(Output('datepicker_report_section','style'),
              [Input('checklist_daterange', 'values')])
def pilih_shipper(trigger):
    if len(trigger) == 1:
        return {'display':'block'}
    else:
        return {'display':'none'}

@app.callback([Output('download_data_excel_section','style'),
                Output('download_data_pdf_section','style')],
              [Input('admin_pilih_jenis_file', 'value')])
def pilih_shipper(jenis_file):
    if jenis_file=="Excel":
        return {'display':'block'}, {'display':'none'}
    else:
        return {'display':'none'}, {'display':'block'}
