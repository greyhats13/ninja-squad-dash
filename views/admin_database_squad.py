import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from dash.dependencies import Input, Output, State
import os
import base64
import io
from server import app, server
from datetime import datetime
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


layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_upload_squad', refresh=True),
                html.H3("Ninja Squad Data", style={'text-align':'center'}),
                html.Div(
                    className="twelve columns",
                    style={'padding-bottom':'15px'},
                    children=[
                        dt.DataTable(
                            rows=[{}],
                            columns=['code','name','created_at'],
                            filterable=True,
                            row_selectable=True,
                            sortable=True,
                            selected_row_indices=[],
                            id='admin_squadlist-table')
                    ]
                ),
                html.Hr(),
                html.Br(),
                html.H3('Upload New Squad', style={'text-align':'center'}),
                html.Div(id='hide-squad-id', style={'display':'none'}),
                dcc.Upload(
                    id='upload-squad-data',
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
                html.Div(id='hasil-squad', style={'text-align': 'center'}),
                html.Br(),
                html.Hr(),

                html.H3('Pull New Squad', style={'text-align':'center'}),
                html.Button(
                    id='pull_squad_button',
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
                html.Div(id='hasil_pull_squad', style={'text-align': 'center'}),
            ]
        )
    ]
)

@app.callback(
    Output('hasil_pull_squad', 'children'),
    [Input('pull_squad_button', 'n_clicks'),
    Input('hide-squad-id', 'children')])
def pull_data(klik_edit_shipment, squad_id):
    if klik_edit_shipment > 0:
        with open("./data/query_squad.txt") as file:
            query = file.read()
        query = query.replace('{{placeholder}}',str(squad_id))
        query = "data:text/plain;charset=utf-8,%EF%BB%BF" + quote(query)

        return (html.A('Klik di sini buat generate query untuk narik datanya.', href=query, target="_blank"), ' Setelah dicopy, bisa dipaste ke text box (hapus dulu textboxnya biar kosong) yang ada di ', html.A('link ini, lalu klik Tombol Execute', href='https://redash.ninjavan.co/queries/6064/source', target="_blank"), '. Lalu, download as Excel atau CSV, dan upload lewat tombol di atas.')

@app.callback(
    [Output('admin_squadlist-table','rows'),
    Output('hide-squad-id', 'children'),
    Output('hasil-squad', 'children')],
    [Input('upload-squad-data', 'filename'),
    Input('upload-squad-data', 'contents'),
    Input('url_upload_squad','pathname')])
def update_output(filename,contents,trigger):
    squad = pd.read_pickle('./data/squad.pkl')
    if contents is not None:
        try:
            data = parse_contents(contents, filename)
            data.created_at = pd.to_datetime(data.created_at)
            squad = pd.concat([squad,data], sort=False)
            squad = squad.drop_duplicates('id',keep='last')
            squad = squad.sort_values(by='id').reset_index(drop=True)
            squad.to_pickle('./data/squad.pkl')
            rows = squad.to_dict('records')
            return rows, squad.id.max(), 'Sukses.'
        except Exception as ex:
            rows = squad.to_dict('records')
            return rows, squad.id.max(), 'Hmmm, ada error. Coba cek datanya dulu. Error : '+str(ex)
    else:
        rows = squad.to_dict('records')
        return rows, squad.id.max(), ''
