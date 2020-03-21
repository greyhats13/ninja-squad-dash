import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from server import app, User
import dash_table_experiments as dt
import pandas as pd
from datetime import datetime, timedelta

layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_admin_holiday_date', refresh=True),
                html.H3('Blocked Dates (Holiday) Management ', style={'text-align':'center'}),
                html.Div(
                children=[html.Div(html.H5('Pilih tanggal liburan :'), className='six columns'),
                html.Div([dcc.Dropdown(
                    id='admin_pilih-tahun-liburan',
                    options=[{'label': i, 'value': str(i)} for i in range(2017,2031)],
                    value=str(datetime.today().year))
                    ], className="six columns", style={'padding-top':'6.5px'}
                )], className='row', style={'padding-bottom':'6.5px'}),
                html.Div(
                    children=[
                        html.Div([
                        dcc.DatePickerSingle(
                            month_format='MMM Do, YY',
                            placeholder='MMM Do, YY',
                            id = 'choose_holiday',
                            date=datetime.today().date()
                        ),
                        html.Br(),
                        html.Button(
                            children='Update',
                            n_clicks_timestamp=0,
                            type='submit',
                            id='update_holiday',
                            style={'background-color':'#138d75', 'color':'white'}
                        ),
                        html.Br(),
                        html.Div(children='Pilih tanggal di tabel di samping lalu tekan tombol Delete.'),
                        html.Button(
                            children='Delete',
                            n_clicks_timestamp=0,
                            type='submit',
                            id='delete_holiday_date',
                            style={'background-color':'#ff2020', 'color':'white'}
                        )
                        ], className="six columns"),
                        html.Div(
                            className="six columns",
                            children=[
                                dt.DataTable(
                                    rows=[{}],
                                    columns=['date'],
                                    sortable=False,
                                    row_selectable=True,
                                    selected_row_indices=[],
                                    id='holiday_table')
                            ]
                        )
                    ], className="row"
                )
            ]
        )
    ]
)

# Create callbacks
@app.callback(Output('holiday_table', 'rows'),
              [Input('admin_pilih-tahun-liburan', 'value'),
              Input('update_holiday', 'n_clicks_timestamp'),
              Input('delete_holiday_date', 'n_clicks_timestamp')],
              [State('choose_holiday', 'date'),
              State('holiday_table', 'selected_row_indices')])
def tahun_holiday(tahun, klik_update, klik_hapus, tanggal, selected_row_indices):
    holiday = pd.read_pickle("./data/holiday.pkl")
    temp = pd.read_pickle("./data/holiday_temp.pkl")
    if (int(klik_update)==temp[0].iloc[0] and int(klik_hapus)==temp[0].iloc[1]):
        holi = holiday[holiday.date.str[:4]==tahun].sort_values(by='date')
        rows = holi.to_dict('records')
        return rows
    else:
        if int(klik_update) > int(klik_hapus):
            holiday = holiday.append({'date': tanggal}, ignore_index=True)
            holiday = holiday[['date']].drop_duplicates().sort_values(by='date').reset_index(drop=True)
            holiday.to_pickle("./data/holiday.pkl")
            pd.DataFrame([int(klik_update),int(klik_hapus)]).to_pickle("./data/holiday_temp.pkl")
            holi = holiday[holiday.date.str[:4]==tahun]
            rows = holi.to_dict('records')
            return rows
        elif int(klik_hapus) > int(klik_update):
            if len(selected_row_indices)==0:
                pass
            else:
                list_hapus = holiday[holiday.date.str[:4]==tahun].iloc[selected_row_indices].date
                holiday = holiday[~holiday.isin(list(list_hapus))].dropna()
                selected_row_indices = []
                holiday.to_pickle("./data/holiday.pkl")
                pd.DataFrame([int(klik_update),int(klik_hapus)]).to_pickle("./data/holiday_temp.pkl")
                holi = holiday[holiday.date.str[:4]==tahun].sort_values(by='date')
                rows = holi.to_dict('records')
                return rows
        else:
            holi = holiday[holiday.date.str[:4]==tahun].sort_values(by='date')
            rows = holi.to_dict('records')
            return rows
