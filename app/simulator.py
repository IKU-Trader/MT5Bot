# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:41:14 2023

@author: IKU-Trader
"""
import os
import sys


import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from libs.time_utils import TimeUtils
from libs.utils import Utils
from libs.const import const
from .market_data import MarketData
from libs.data_server_stub import DataServerStub
from libs.data_buffer import DataBuffer, ResampleDataBuffer
from libs.technical_analysis import TA
from datetime import datetime


TICKERS = ['GBPJPY', 'GBPAUD']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H2', 'H4']
BARSIZE = ['100', '200', '300', '400', '500']
YEARS = ['2017', '2018', '2019', '2020', '2021', '2022', '2023']

INTERVAL_MSEC_LIST = [100, 200, 500, 1000]
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

#
server = DataServerStub('')

# ----

timer = dcc.Interval(id='timer', interval=INTERVAL_MSEC_LIST[0], disabled=True)

setting_bar = dbc.Row( [html.H5('Control',
                        style={'margin-top': '2px', 'margin-left': '24px'})
                        ],
                        style={"height": "3vh"},
                        className='bg-primary text-white')

ticker_dropdown = dcc.Dropdown(id='symbol_dropdown',
                               multi=False,
                               value=TICKERS[0],
                               options=[{'label': x, 'value': x} for x in TICKERS],
                               style={'width': '140px'})

ticker = html.Div([ html.P('Ticker Symbol',
                           style={'margin-top': '8px', 'margin-bottom': '4px'}, 
                           className='font-weight-bold'),
                           ticker_dropdown])
 
timeframe_dropdown = dcc.Dropdown(id='timeframe_dropdown', 
                                  multi=False, 
                                  value=TIMEFRAMES[1], 
                                  options=[{'label': x, 'value': x} for x in TIMEFRAMES],
                                  style={'width': '120px'})

timeframe = html.Div([ html.P('Time Frame',
                       style={'margin-top': '8px', 'margin-bottom': '4px'},
                       className='font-weight-bold'),
                       timeframe_dropdown])


year_dropdown = dcc.Dropdown(id='year', 
                                  multi=False, 
                                  value=YEARS[-1], 
                                  options=[{'label': x, 'value': x} for x in YEARS],
                                  style={'width': '120px'})

month_from_dropdown = dcc.Dropdown(id='month_from', 
                                  multi=False, 
                                  value='1', 
                                  options=[{'label': x, 'value': x} for x in range(1, 13)],
                                  style={'width': '120px'})

month_to_dropdown = dcc.Dropdown(id='month_to', 
                                  multi=False, 
                                  value='1', 
                                  options=[{'label': x, 'value': x} for x in range(1, 13)],
                                  style={'width': '120px'})

term = html.Div([ html.P('Year',
                          style={'margin-top': '8px', 'margin-bottom': '4px'},
                          className='font-weight-bold'),
                  year_dropdown,
                  html.P('Month',
                          style={'margin-top': '8px', 'margin-bottom': '4px'},
                          className='font-weight-bold'),                  
                  month_from_dropdown,     
                  html.P('～',
                       style={'margin-top': '8px', 'margin-bottom': '4px'},
                       className='font-weight-bold'),
                  month_to_dropdown])

load = html.Div([ html.Button(id='load_button', 
                              n_clicks=0, 
                              children='Load Data',
                              style={'margin-top': '4px', 'margin-left': '8px', 'margin-right': '16px'},
                              className='btn btn-primary'),
                  html.Div(id='load_response', 
                           children='-',
                           style={'margin-top': '4px', 'margin-left': '8px', 'margin-bottom': '4px'})])

barsize_dropdown = dcc.Dropdown(id='barsize_dropdown', 
                                multi=False, 
                                value=BARSIZE[2],
                                options=[{'label': x, 'value': x} for x in BARSIZE],
                                style={'width': '120px'})

barsize = dbc.Col([html.P('Display Bar Size',
                          style={'margin-bottom': '4px'}),
                           barsize_dropdown])

replay = html.Div([html.P('Replay'),
                   dbc.Row([
                            html.P('Timer Interval(msec)', style={'margin-top': '4px', 'margin-bottom': '4px'}),
                            dcc.Dropdown(id='timer_interval', 
                                     multi=False, 
                                     value = INTERVAL_MSEC_LIST[0],
                                     options = INTERVAL_MSEC_LIST,
                                     style={'width': '120px'}),
                            html.P('bar', style={'margin-top': '8px', 'margin-bottom': '0px'}),
                            dcc.Input(id="bar_index",
                                      type="number",
                                      placeholder="index",
                                      value=0,
                                      min=0,
                                      step=1,
                                      style={'width':'120px', 'margin-top':'4px', 'margin-left': '12px'})]),
                            html.Button(id='play_button', n_clicks=0, children='Play',
                                                        style={'margin-top': '8px', 'margin-left': '0px'},
                                                        className='btn btn-primary'),
                            html.Button(id='stop_button', n_clicks=0, children='Stop',
                                                        style={'margin-top': '8px', 'margin-left': '4px'},
                                                        className='btn btn-primary')
                    ])

sidebar = html.Div([   setting_bar,
                        html.Div([ticker,
                                 timeframe,
                                 html.Hr(),
                                 term,
                                 load,
                                 html.Hr(),
                                 barsize,
                                 html.Hr(),
                                 replay],
                        style={'height': '100vh', 'margin': '2px'})])
    
contents = html.Div([   dbc.Row([html.H5('MetaTrader5', style={'margin-top': '2px', 'margin-left': '20px'})],
                                style={"height": "3vh"}, className='bg-primary text-white'),
                        dbc.Row([html.Div(id='chart_output')]),
                        timer
                    ])

app.layout = dbc.Container([dbc.Row([dbc.Col(sidebar, width=2, className='bg-light'),
                                     dbc.Col(contents, width=9)],
                                     style={"height": "80vh"})],
                            fluid=True)

@app.callback([ Output('load_button', 'n_clicks'),
                Output('bar_index', 'value'),
                Output('load_response', 'children')],
              [ Input('load_response', 'children'),
                Input('load_button', 'n_clicks')],
              [ State('symbol_dropdown', 'value'),
                State('timeframe_dropdown', 'value'),
                State('year', 'value'),
                State('month_from', 'value'),
                State('month_to', 'value')]
                )
def updateServer(response, n_clicks,  symbol, timeframe, year, month_from, month_to):
    global server
    global buffer
    print(n_clicks)
    if n_clicks == 0:
        return (0, 0, response)    
    if timeframe[0].upper() != 'M':
        return (0, 0, 'Bad Timeframe...' + timeframe)
    
    year = int(year)
    month_from = int(month_from)
    month_to = int(month_to)
    if month_from > month_to:
        return (0, 0, 'Bad Month...')
    
    tbegin = TimeUtils.pyTime(year, month_from, 1, 0, 0, 0, TimeUtils.TIMEZONE_TOKYO)    
    month_from -= 1
    if month_from <= 0:
        month_from += 12
        year_from = year - 1
        year_to = year
    else:
        year_from = year
        year_to = year
    
    print(f'Read begin {year_from}/{month_from} - {year_to}/{month_to}')
    
    minutes = int(timeframe[1:])
    candles, tohlc = MarketData.fxData(symbol, year_from, month_from, year_to, month_to, 1)
    if len(tohlc[0]) < 0:
        return (0, 0, 'Read error, No data')

    bar_index =-1
    for i, t in enumerate(tohlc[0]):
        if t >= tbegin:
            bar_index = i
            break    
    if bar_index < 0:
        return(0, 0, 'No data found')
    
    server = DataServerStub('')
    server.importData(tohlc)
    tohlc2 = server.init(bar_index, step_sec=10)
    buffer = ResampleDataBuffer(tohlc2, TA.basic_kit(), minutes)
    return (0, bar_index, str(server.size()))

@app.callback([Output('play_button', 'n_clicks'),
                Output('stop_button', 'n_clicks'),
                Output('timer', 'interval'),
                Output('timer', 'disabled')],
              [Input('play_button', 'n_clicks'),
                Input('stop_button', 'n_clicks')],
              [State('timer_interval', 'value'),
                State('timer', 'disabled')])
def stop_interval(n_play, n_stop, timer_interval, disabled):
    if n_play is None or n_stop is None:
        return (0, 0, timer_interval, disabled)
    if n_play == 0 and n_stop == 0:
        return (0, 0, timer_interval, disabled)
    if n_play > 0:
        print('Play')
        return (0, 0, timer_interval, False)
    if n_stop > 0:
        print('Stop')
        return (0, 0, timer_interval, True)

@app.callback(  Output('chart_output', 'children'),
                 Input('timer', 'n_intervals'),
                 State('symbol_dropdown', 'value'),
                 State('timeframe_dropdown', 'value'),
                 State('barsize_dropdown', 'value'),
                 State('bar_index', 'value')
)
def updateChart(interval, symbol, timeframe, display_bar_size, bar_index):
    try:
        if server.size() == 0:
            print('No data')
            return no_update
    except:
        print('No data')
        return no_update
    #print(interval)
    num_bars = int(display_bar_size)
    bar_index = int(bar_index)
    print(symbol, timeframe, num_bars, bar_index)
    candles = server.nextData()
    t0 = datetime.now()
    buffer.update(candles)
    _, dic = buffer.temporary()
    sliced = Utils.sliceDicLast(dic, num_bars)
    print('Elapsed time: ', datetime.now() - t0)
    chart = createChart(symbol, timeframe, sliced)
    return chart
  
def createChart(symbol, timeframe, dic):
    fig = create_candlestick(dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    time = dic[const.TIME]
    n = len(time)
    #print(symbol, timeframe, dic)
    xtick0 = (5 - time[0].weekday()) % 5
    tfrom = time[0].strftime('%Y-%m-%d %H:%M')
    tto = time[-1].strftime('%Y-%m-%d %H:%M')
    if timeframe == 'D1' or timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%d/%H:%M'
    fig['layout'].update({
                            'title': symbol + '　' +  tfrom + '  ...  ' + tto,
                            'width': 1200,
                            'height': 600,
                            'xaxis':{
                                        'title': '',
                                        'showgrid': True,
                                        'ticktext': [x.strftime(form) for x in time][xtick0::5],
                                        'tickvals': np.arange(xtick0, len(time), 5)
                                    },
                            'yaxis':{
                                        'title': '',
                                        'tickformat': 'digit'
                                    },
                            'margin': {'l':2, 'r':10, 'b' :40, 't':70, 'pad': 2},
                            'paper_bgcolor': '#f7f7ff' # RGB
                        })
    
    #fig.add_trace(go.Scatter(x=np.linspace(0, 1, n), y=dic['SMA5'], mode='lines', name='SMA5'))
    return dcc.Graph(id='stock-graph', figure=fig)



def createTable(df):
    table = dash_table.DataTable(style_cell={'textAlign':'center', 
                                             'maxWidth':'80px', 
                                             'minWidth':'40px', 
                                             'whiteSpace':'normal' ,
                                             'height': 'auto',
                                             'font_family': 'sans-serif',
                                             'font_size': '12px'},
                                 style_data={'color':'black','backgroundColor':'white'},
                                 style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'rgb(220,220,220)'}],
                                 style_header={'backgroundColor':'rgb(72,72,128)','color':'white','fontWeight':'bold'},
                                 fixed_rows={'headers':True},   
                                 style_table={'minWidth':'90%'},
                                 columns=[{'name':col, 'id':col} for col in df.columns],
                                 data=df.to_dict('records'),
                                 page_size=10,
                                 export_format='csv')
    return table

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)

