import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import users_mgt as um

import copy
import base64
import io
import pandas as pd

from dash.dependencies import Input, Output, State
from validate_email import validate_email

import new_user as nu
from server import app

warnings.filterwarnings("ignore")

# file upload function
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), header=None)
            df.columns = ['Fullname', 'Username', 'Email']
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), header=None)
            df.columns = ['Fullname', 'Username', 'Email']

    except Exception as e:
        print(e)
        return None

    return df

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_admin_db', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(className="bingkaiteks",
                            children=[
                                html.H5("Tambahkan Squad")
                            ],
                            style={
                            'text-align': 'center',
                            'padding-top': '10px',
                            'margin-bottom': '12px'
                        })
                    ]
                ),
            ),
        html.Div("""Masukkan jumlah Squad yang diinginkan, atau lakukan upload file XLSX/CSV tanpa header (data dimulai dari row 1)
        dengan kolom 1 : Fullname, kolom 2 : Username, dan kolom 3 : Email.""", className='twelve columns', style={'margin-bottom':'25px'}),
        # html.Hr(),
        html.Div(
            # method='Post',
            className="row",
            children=[
                html.Div('Mau input berapa squad?', className='four columns'),
                dcc.Input(
                    placeholder='e.g: 5',
                    type='text',
                    n_submit=0,
                    id='admin_squadnumb-box',
                    className="four columns",
                    style={'margin-bottom':'8px'}
                ),
                html.Button(
                    children='Lanjut',
                    n_clicks=0,
                    type='submit',
                    id='admin_add-squad-button',
                    className="four columns",
                    style={'background-color':'#a93226', 'color':'white'}
                )
            ]
        ),
        dcc.Upload(
            id='admin_upload-data',
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
            },
            multiple=False),
        html.Div([
            html.Div(
                children=dt.DataTable(
                    rows=[],
                    columns=['Fullname', 'Username', 'Email'],
                    editable=True,
                    filterable=False,
                    sortable=False,
                    id='editable-table'
                ),
                className='twelve columns',
                style={'margin-bottom':'12px'}
            )
        ]),
        html.Div(
            className="row",
            children=[
                html.Button(
                    children='Tambahkan Squad',
                    n_clicks=0,
                    type='submit',
                    id='admin_submit-squad-button',
                    className="twelve columns",
                    style={'background-color':'#a93226', 'color':'white'}
                )
            ]
        )
        ]
    )
])

@app.callback(
    [Output('url_admin_db', 'pathname'),
    Output('editable-table', 'rows')],
    [Input('editable-table', 'row_update'),
    Input('admin_add-squad-button', 'n_clicks'),
    Input('admin_submit-squad-button', 'n_clicks'),
    Input('admin_squadnumb-box', 'n_submit'),
    Input('admin_upload-data', 'contents'),
     Input('admin_upload-data', 'filename')],
    [State('editable-table', 'rows'),
    State('admin_squadnumb-box', 'value')])
def update_rows(row_update, klik_tambah, klik_submit, enter_tambah, contents, filename, rows, input_num):
    if klik_submit > 0:
        something_bad_happened = 0
        if type(input_num) != int:
            input_num = len(rows)
        for i in range(int(input_num)):
            try:
                if validate_email(rows[i]['Email']) == True:
                    um.add_user(rows[i]['Fullname'], rows[i]['Username'], 'NinjaSqu4d', rows[i]['Email'].lower())
                    token = nu.randomStringDigits(16)+rows[i]['Email'].lower().split('@')[0]+'&'+rows[i]['Username']
                    nu.kirimemail(rows[i]['Email'].lower(), token, rows[i]['Fullname'])
                else:
                    something_bad_happened = 1
                    pass
            except:
                # continue
                return '/admin-failed', []
        if something_bad_happened == 1:
            return '/admin-success-w-exc', []
        else:
            return '/admin-success', []
        # return None, [], 'Sukses menambahkan '+', '.join(str(uname) for uname in daftar_nama)
    if (klik_tambah > 0) or (enter_tambah > 0):
        if (rows == None) or (len(rows)!=int(input_num)):
            records = [{'Fullname': '', 'Username': '', 'Email': ''} for i in range(int(input_num))]
            return None, records
        else:
            if contents is not None:
                df = parse_contents(contents, filename)
                if df is not None:
                    return None, df.to_dict('records')
                else:
                    return None, [{}]
            else:
                row_copy = copy.deepcopy(rows)
                return None, row_copy
    else:
        if contents is not None:
            df = parse_contents(contents, filename)
            if df is not None:
                return None, df.to_dict('records')
            else:
                return None, [{}]
        else:
            return None, rows
