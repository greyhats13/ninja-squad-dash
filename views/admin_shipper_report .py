import dash_core_components as dcc
import dash_html_components as html
import time
import requests
import pandas as pd
from dash.dependencies import Input, Output, State
import os
import base64
import io
from tqdm import tqdm
from server import app, server

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
                html.H3('Generate Weekly Shipment Report', style={'text-align':'center'}),
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
                html.H5(id='hasil', style={'text-align': 'center'})
            ]
        )
    ]
)

@app.callback(
    Output('hasil', 'children'),
    [Input('upload-data', 'filename'),
    Input('upload-data', 'contents')])
def update_output(filename,contents):
    kode = pd.read_csv('./data/postcode.csv', index_col='id')
    kode = kode.drop_duplicates('to_postcode', keep='last')
    try :
        if contents is not None:
            data = parse_contents(contents, filename)
            data.to_postcode = data.to_postcode.replace("-","0")
            data.to_postcode = data.to_postcode.fillna('0').astype('str').apply(lambda s: (s.encode('ascii', 'ignore')).decode("utf-8"))
            data.to_postcode = data.to_postcode.astype(float).astype(int)
            data = pd.merge(data,kode[['kecamatan','kabupaten','to_postcode']],on='to_postcode',how='left')
            data.submitted_weight = data.submitted_weight.replace('\n"',"",regex=True)

            data.order_creation_datetime = pd.to_datetime(data.order_creation_datetime)
            data.pod_datetime = pd.to_datetime(data.pod_datetime)
            data['1st_attempt_at'] = pd.to_datetime(data['1st_attempt_at'])
            data['2nd_attempt_at'] = pd.to_datetime(data['2nd_attempt_at'])
            data['3rd_attempt_at'] = pd.to_datetime(data['3rd_attempt_at'])
            namashipper = data['shipper_name'][0]
            data = data.drop(['shipper_name','delivery_fee_origin'], axis=1)
            reindeks = ["order_creation_datetime","tracking_id","granular_status","delivery_address","to_postcode","kecamatan","kabupaten","submitted_weight","actual_weight","parcel_size","width","height","length","order_comments","pod_datetime","pod_recipient_name","pod_photo_url","pod_signature_url","1st_attempt_at","first_fail_reason","2nd_attempt_at","second_fail_reason","3rd_attempt_at","third_fail_reason","delivery_fee"]
            data = data.reindex(columns = reindeks)

            strIO = io.BytesIO()
            writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
            data.to_excel(writer, sheet_name="result", startrow=4, index=False)
            # writer.save()

            worksheet = writer.sheets["result"]
            workbook  = writer.book
            tebal = workbook.add_format({'bold': True})
            bulatkan = workbook.add_format({'num_format': '_(* #,##0_);_(* \(#,##0\);_(* "-"??_);_(@_)'})
            worksheet.set_column('Y:Y', None, bulatkan)
            for j, width in enumerate(get_col_widths(data)):
                worksheet.set_column(j-1, j-1, width)
            worksheet.write(0, 0, "PT. Andiarta Muzizat", tebal)
            worksheet.write(1, 0, "Shipment Report", tebal)
            worksheet.write(2, 0, "Nama Shipper : " + namashipper, tebal)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('P:P', 20)
            worksheet.set_column('Q:Q', 20)
            worksheet.set_column('R:R', 20)

            writer.save()

            csv_string = strIO.getvalue()
            strIO.seek(0)

            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file = base64.b64encode(strIO.read()).decode("utf-8")
            excel = f'data:{media_type};base64,{file}'

            return ('Sudah selesai gannnn.', html.A('Klik di sini buat download.', href=excel))
    except:
        return ('Ada error nih. Coba upload file yang benernya.')
