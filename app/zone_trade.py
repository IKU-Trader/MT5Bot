# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:31:39 2023

@author: IKU-Trader
"""

import os
import sys

import polars as pl
from polars import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

from libs.utils import Utils
from libs.time_utils import TimeUtils
from libs.data_buffer import ResampleDataBuffer
from market_data import MT5Data
from libs.candle_chart import CandleChart, BandPlot, makeFig, gridFig, Colors
from libs.technical_analysis import TA
from libs.converter import Converter
from libs.const import const

def minmax(array):
    a = np.array(array, dtype=float)
    try:
        minv = np.nanmin(a)
        maxv = np.nanmax(a)
        if np.isnan(minv) or np.isnan(maxv):
            return None
        else:
            return (minv, maxv)
    except:
        return None
    
def plotChart(ticker: str, df: DataFrame):
    time = df[const.TIME]
    fig, axes = gridFig([8, 4, 2, 2, 1], (14, 15))
    chart1 = CandleChart(fig, axes[0], title=ticker, write_time_range=True)
    chart1.drawCandle(time, df[const.OPEN], df[const.HIGH], df[const.LOW], df[const.CLOSE], ymargin=0.5)
    chart1.drawLine(time, df['SMA5'])
    chart1.drawLine(time, df['SMA20'], color='green')
    chart1.drawLine(time, df['SMA60'], color='blue')
    chart1.drawLine(time, df['H2_SMA20'], color='yellow', linewidth=2.0)
    chart1.drawLine(time, df['H4_SMA20'], color='orange', linewidth=2.0)
    chart1.drawLine(time, df['D1_SMA5'], color='purple', linewidth=3.0)
    chart1.drawLine(time, df['BOLLINGER+'], color='gray', linewidth=0.5)
    chart1.drawLine(time, df['BOLLINGER-'], color='gray', linewidth=0.5)
    chart1.drawMarkers(time, df[const.LOW], -0.05, df['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(time, df[const.LOW], -0.05, df['SIGNAL'], 2, '^', 'green', overlay=2, markersize=20)
    chart1.drawMarkers(time, df[const.HIGH], 50, df['SIGNAL'], -1, '^', 'red', overlay=1, markersize=20)
    chart1.drawMarkers(time, df[const.HIGH], 50, df['SIGNAL'], -2, '^', 'red', overlay=2, markersize=20)
    
    #chart2 = CandleChart(fig, axes[1], title=ticker, write_time_range=True)
    #chart2.drawLine(time, df['D1_SMA5'], color='purple', linewidth=2.0)
    
    chart2 = CandleChart(fig, axes[1], comment='SLOPE')
    chart2.drawLine(time, df['SLOPE_SMA5'], color='red')
    chart2.drawLine(time, df['SLOPE_SMA60'], color='blue')
    chart2.drawLine(time, df['SLOPE_SMA20'], color='green')
    chart2.drawLine(time, df['SLOPE_SMA60'], color='blue')
    
    chart3 = CandleChart(fig, axes[2], comment='ATR')
    chart3.drawLine(time, df['ATR'])
    
    chart4 = CandleChart(fig, axes[3], comment='ADX')
    chart4.drawLine(time, df['ADX'])
    
    chart5 = CandleChart(fig, axes[4], comment='MA Trend', date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
    colors = {TA.UPPER_TREND: 'red',
              TA.UPPER_SUB_TREND: Colors.light_red,
              TA.UPPER_DIP: 'black',
              TA.LOWER_TREND: 'green',
              TA.LOWER_SUB_TREND: Colors.light_green,
              TA.LOWER_DIP: 'black',
              TA.NO_TREND: 'gray'}
    chart5.drawBand(time, df['MA_TREND'], colors=colors, xlabel=True)

def displayChart(ticker: str,
                 dic: dict,
                 from_year: int, 
                 from_month: int, 
                 to_year: int, 
                 to_month: int, 
                 from_hour: int, 
                 to_hour: int):
    
    time = dic[const.TIME]
    t_begin = TimeUtils.pyTime(from_year, from_month, 1, from_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    t_end = TimeUtils.pyTime(to_year, to_month, 1, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    t_end += timedelta(days=1)
    t = t_begin
    while t <= t_end:
        t1 = TimeUtils.pyTime(t.year, t.month, t.day, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
        if to_hour < from_hour:
            t1 += timedelta(days=1)
        n, begin, end = TimeUtils.sliceTime(time, t, t1)
        if n >= 50:
            print(t, 'size:', n)
            oneday = Utils.sliceDic(dic, begin, end)
            plotChart(ticker, oneday)
        t += timedelta(days=1)



def main():
    ticker = 'GBPJPY'
    mt5 = MT5Data(r'..\market_data\mt5\gemforex\M1')
    df = mt5.importFromCsv('GBPJPY', 'M1')
    #print(dic['H4'][1000:1050])
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    tohlcv = Converter.df2dic(df)
    buffer = ResampleDataBuffer(tohlcv, TA.full_kit(), 5)
    
    displayChart(ticker, buffer.dic, 2023, 1, 2023, 5, 7, 2)
       
if __name__ == '__main__':
    main()