# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:41:14 2023

@author: IKU-Trader
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../Utilities'))

import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from py_mt5 import PyMT5
from time_utils import TimeUtils
from const import const

INTERVAL_MSEC = 200
TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
BARSIZE = ['50', '100', '150', '200', '300', '400', '500']

account_info = None
server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

TYPE_BUY = 0 
TYPE_SELL = 1

# ----
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

timeframe =  html.Div([ html.P('Time Frame',
                        style={'margin-top': '16px', 'margin-bottom': '4px'},
                        className='font-weight-bold'),
                        timeframe_dropdown])

barsize_dropdown = dcc.Dropdown(id='barsize_dropdown', 
                                multi=False, 
                                value=BARSIZE[2],
                                options=[{'label': x, 'value': x} for x in BARSIZE],
                                style={'width': '120px'})

barsize = html.Div([html.P('Display Bar Size',
                    style={'margin-top': '16px', 'margin-bottom': '4px'},
                    className='font-weight-bold'),
                    barsize_dropdown])

market_order = html.Div([html.P('Entry (Market Order)',
                         style={'margin-top': '8px', 'margin-bottom': '4px'}, 
                         className='font-weight-bold'),
                         
                         dcc.Input(id="market_order_lot", type="number", placeholder="lot",
                                   min=0.1, max=100, step=0.1,
                                   style={'margin-top': '8px'}),
                         html.Button(id='buy_market_order_button', n_clicks=0, children='Buy',
                                     style={'margin-top': '4px', 'margin-left': '16px', 'margin-right': '8px'},
                                     className='btn btn-primary'),
                         html.Button(id='sell_market_order_button', n_clicks=0, children='Sell',
                                     style={'margin-top': '4px', 'margin-right': '8px'},
                                     className='btn btn-primary'),
                         html.Div(id='market_order_response', children='')
                    ])

close_order = html.Div([html.P('Close Order',
                        style={'margin-top': '8px', 'margin-bottom': '4px'}, 
                        className='font-weight-bold'),
                        html.Div([dcc.Dropdown(id='order_ticket_dropdown', 
                                               multi=False, 
                                               style={'width': '120px'}),

                                  dcc.Input(id="close_lot", type="number", placeholder="lot",
                                            min=0.1, max=100, step=0.1,
                                            style={'margin-top': '8px'}),
                                  html.Button(id='close_apply_button', n_clicks=0, children='Close',
                                              style={'margin-top': '4px', 'margin-left': '16px', 'margin-right': '16px'},
                                              className='btn btn-primary')]),
                                  html.Div([html.Button(id='close_all_button', n_clicks=0, children='Close All',
                                                        style={'margin-top': '4px', 'margin-right': '16px'},
                                                        className='btn btn-primary'),
                                  html.Div(id='close_order_response', children='')])
                                ])

sidebar =  html.Div([   setting_bar,
                        html.Div([ticker,
                                 timeframe,
                                 barsize,
                                 html.Hr(),
                                 market_order,
                                 html.Hr(),
                                 close_order],
                        style={'height': '100vh', 'margin': '2px'})])
    
contents = html.Div([   dbc.Row([html.H5('MetaTrader5', style={'margin-top': '2px', 'margin-left': '20px'})],
                                style={"height": "3vh"}, className='bg-primary text-white'),
                        dbc.Row([html.Div(id='chart_output'),
                                 html.P('Account',
                                        style={'margin-top': '4px', 'margin-bottom': '2px'}, 
                                        className='font-weight-bold'),
                                 html.Div([],
                                          id='account_info',
                                          style={'height': '5vh', 'width': '130vh', 'margin-left': '20px'}),
                                          html.Div(id='account_table'),
                                          html.P('Position',
                                                  style={'margin-top': '50px', 'margin-bottom': '2px'}, 
                                                  className='font-weight-bold'),
                                html.Div([],
                                          id='position_info',
                                          style={'height': '5vh', 'width': '130vh', 'margin-left': '20px'}),
                                html.Div(id='position_table')                                    
                                    
                            ]),
                        dcc.Interval(   id='timer',
                                        interval=INTERVAL_MSEC,
                                        n_intervals=0)
                    ])

app.layout = dbc.Container([dbc.Row([dbc.Col(sidebar, width=2, className='bg-light'),
                                     dbc.Col(contents, width=9)],
                                     style={"height": "80vh"})],
                            fluid=True)

@app.callback(
    [Output('market_order_response', 'children'),
     Output('buy_market_order_button', 'n_clicks'),
     Output('sell_market_order_button', 'n_clicks'),
    ],
    Input('buy_market_order_button', 'n_clicks'),
    Input('sell_market_order_button', 'n_clicks'),
    State('market_order_lot', 'value'), 
    State('symbol_dropdown', 'value')
)
def update_market_order(buy_n_clicks, sell_n_clicks, lot, symbol):
    #print(buy_n_clicks, sell_n_clicks, lot, symbol)
    if buy_n_clicks == 0 and sell_n_clicks == 0:
        return ('', 0, 0)
    lot = float(lot)
    if buy_n_clicks > 0:    
        ret, dic = server.buyMarketOrder(symbol, lot)
    
    if sell_n_clicks > 0:
        ret, dic = server.sellMarketOrder(symbol, lot)
        
    if ret:
        return ('Success', 0, 0)
    else:
        return ('Fail retcode: ' + str(dic['retcode']), 0, 0)
    
@app.callback(
    Output('close_order_response', 'children'),
    Output('close_apply_button', 'n_clicks'),
    Output('close_all_button', 'n_clicks'),
    Input('close_apply_button', 'n_clicks'),
    Input('close_all_button', 'n_clicks'),
    State('symbol_dropdown', 'value'),
    State('close_lot', 'value'),
    State('order_ticket_dropdown', 'value'), 
)
def update_close_order(close_n_clicks, close_all_n_clicks, symbol, lot, ticket):
    #print(close_n_clicks, close_all_n_clicks,symbol, ticket, lot)
    if close_n_clicks == 0 and close_all_n_clicks == 0:
        return ('', 0, 0)
    
    if close_all_n_clicks > 0:
        server.closeAll('')
        print('Close all')
        return ('', 0, 0)
    
    lot = float(lot)
    ticket = int(ticket)
    dic = server.position(ticket)
    if dic is None:
        return ('Fail No position of ticket', 0, 0)
    #print(dic)
    pos_time = TimeUtils.timestamp2localtime(dic['time'], tzinfo=TimeUtils.TIMEZONE_TOKYO)
    pos_symbol = dic['symbol']
    pos_type = dic['type']
    pos_volume = float(dic['volume'])
    pos_profit = dic['profit']
    pos_current_price = dic['price_current']
    
    if symbol != pos_symbol:
        return ('Fail No Ticker symbol of the ticket', 0, 0)
    
    if pos_volume < lot:
        return ('Fail volume is ' + str(pos_volume) , 0, 0)
    
    #print('lot', lot, pos_volume)
    
    if pos_type == TYPE_BUY:
        ret, dic = server.closeBuyPositionMarketOrder(symbol, lot, ticket)
    elif pos_type == TYPE_SELL:
        ret, dic = server.closeSellPositionMarketOrder(symbol, lot, ticket)
    if ret:
        return ('Success', 0, 0)
    else:
        return ('False retcode: ' + str(dic['retcode']), 0, 0)
        
@app.callback([  Output('chart_output', 'children'),
                 Output('account_info', 'children'),
                 Output('position_info', 'children'),
                 Output('order_ticket_dropdown', 'options')],
                 Input('timer', 'n_intervals'),
                 State('symbol_dropdown', 'value'), State('timeframe_dropdown', 'value'), State('barsize_dropdown', 'value')
)
def updateChart(interval, symbol, timeframe, num_bars):
    #print(interval)
    num_bars = int(num_bars)
    #print(symbol, timeframe, num_bars)
    dic = server.download(symbol, timeframe, num_bars)
    chart = createChart(symbol, timeframe, dic)
    if (interval % 10) == 0 or (account_info is None):
        account = accountTable()
    table = positionTable()
    buy_df, sell_df = server.positions('')
    d1 = list(buy_df['ticket'].values)
    d2 = list(sell_df['ticket'].values)
    tickets = []
    if len(d1) > 0:
        tickets += d1
    if len(d2) > 0:
        tickets += d2
    
    options = [{'label': str(x), 'value': str(x)} for x in tickets]
    #print(options)
    return (chart, account, table, options)
  
def createChart(symbol, timeframe, dic):
    fig = create_candlestick(dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    time = dic[const.TIME]
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
                            'width': 1100,
                            'height': 400,
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
    
    #print(fig)
    return dcc.Graph(id='stock-graph', figure=fig)

def accountTable():
    df = server.accountInfo()
    return createTable(df)
    
def positionTable():
    df_buy, df_sell = server.positions('')
    df = pd.concat([df_buy, df_sell])
    return createTable(df)

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
    app.run_server(debug=True, port=3333)
