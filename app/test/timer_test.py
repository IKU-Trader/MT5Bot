# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 08:03:01 2023

@author: IKU
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

INTERVAL_MSEC_LIST = [10, 50, 100, 500, 1000]

# コールバック関数で使用するために`dcc.Interval`を作成
interval = dcc.Interval(id='timer', interval=1000, disabled=False)

# レイアウト
app.layout = html.Div([ dcc.Dropdown(id='timer_interval', 
                                     multi=False, 
                                     value = INTERVAL_MSEC_LIST[2],
                                     options = INTERVAL_MSEC_LIST,
                                     style={'width': '120px'}),
                        dcc.Input(id="index", type="number", placeholder="index",
                                            min=0, step=1,
                                            style={'margin-top': '8px'}),
                        html.Button('Play', id='play_button'),
                        html.Button('Stop', id='stop_button'),
                        interval,
                        html.Div(id='output')
                        ])

# コールバック関数
@app.callback([
                Output('play_button', 'n_clicks'),
                Output('stop_button', 'n_clicks'),
                Output('timer', 'interval'),
                Output('timer', 'disabled')             
                ],
              [
                Input('play_button', 'n_clicks'),
                Input('stop_button', 'n_clicks')],
              [State('timer_interval', 'value'),
                State('timer', 'disabled')])
def stop_interval(n_play, n_stop, timer_interval, disabled):
    if n_play is None or n_stop is None:
        return (0, 0, timer_interval, disabled)
    if n_play == 0 and n_stop == 0:
        return (0, 0, timer_interval, disabled)
    if n_play > 0:
        return (0, 0, timer_interval, False)
    if n_stop > 0:
        return (0, 0, timer_interval, True)
    
@app.callback(Output('index', 'value'),
              [Input('index', 'value'),
              Input('timer', 'n_intervals')])
def update_output(index, n):
    if index is None:
        return 0
    i = int(index)
    return i + 1

if __name__ == '__main__':
    app.run_server(debug=True)