# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 07:54:43 2023

@author: IKU-Trader
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Utilities'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../MarketData'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../CandlestickChart'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../TechnicalAnalysis'))

import numpy as np
import pandas as pd


from time_utils import TimeUtils
from utils import Utils
from const import const
from market_data import MarketData
from data_server_stub import DataServerStub
from data_buffer import DataBuffer, ResampleDataBuffer
from candle_chart import CandleChart, makeFig
from technical_analysis import TA
from datetime import datetime

bar_index = 0
timeframe = 'M5'
symbol = 'GBPJPY'
num_bars = 300
year = 2023
c_month_from=3
c_month_to=4

def load():
    global server
    global buffer

    if timeframe[0].upper() != 'M':
        return (0, 0, 'Bad Timeframe...' + timeframe)
    

    if c_month_from > c_month_to:
        return (0, 0, 'Bad Month...')
    
    tbegin = TimeUtils.pyTime(year, c_month_from, 1, 0, 0, 0, TimeUtils.TIMEZONE_TOKYO)    
    month_from = c_month_from - 1
    month_to = c_month_to
    if month_from <= 0:
        month_from += 12
        year_from = year - 1
        year_to = year
    else:
        year_from = year
        year_to = year
    
    print(f'Read begin {year_from}/{month_from} - {year_to}/{c_month_to}')
    
    minutes = int(timeframe[1:])
    candles, tohlc = MarketData.fxData(symbol, year_from, month_from, year_to, month_to, 1)
    if len(tohlc[0]) < 0:
        return

    bar_index =-1
    for i, t in enumerate(tohlc[0]):
        if t >= tbegin:
            bar_index = i
            break    
    if bar_index < 0:
        return
    
    server = DataServerStub('')
    server.importData(tohlc)
    tohlc2 = server.init(bar_index, step_sec=10)
    buffer = ResampleDataBuffer(tohlc2, TA.basic_kit(), minutes)
    return
    
def update():
    try:
        if server.size() == 0:
            print('No data')
            return
    except:
        print('No data')
        return
    #print(interval)
    
    print(symbol, timeframe, num_bars, bar_index)
    t0 = datetime.now()
    candles = server.nextData()
    buffer.update(candles)
    _, dic = buffer.temporary()
    sliced = Utils.sliceDicLast(dic, num_bars)
    print('Elapsed time: ', datetime.now() - t0)
    
    fig, ax = makeFig(1, 1, (12, 6)) 
    chart = CandleChart(fig, ax, '', '', write_time_range=True)
    time = sliced[const.TIME]
    chart.drawCandle(time, sliced[const.OPEN], sliced[const.HIGH], sliced[const.LOW], sliced[const.CLOSE], xlabel=True)
    chart.drawLine(time, sliced['SMA5'])
    chart.drawLine(time, sliced['SMA20'], color='green')
    chart.drawLine(time, sliced['SMA60'], color='blue')

if __name__ == '__main__':
    load()
    for i in range(10):
        update()