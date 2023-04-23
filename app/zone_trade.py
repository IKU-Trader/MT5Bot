# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:31:39 2023

@author: IKU-Trader
"""

import os
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

from libs.utils import Utils
from libs.time_utils import TimeUtils
from libs.data_buffer import ResampleDataBuffer
from market_data import ClickSecData
from libs.candle_chart import CandleChart, BandPlot, makeFig, gridFig, Colors
from libs.technical_analysis import TA
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
    
def plotChart(ticker: str, dic: dict):
    time = dic[const.TIME]
    fig, axes = gridFig([8, 5, 2, 2, 1], (14, 10))
    chart1 = CandleChart(fig, axes[0], title=ticker, write_time_range=True)
    chart1.drawCandle(time, dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    chart1.drawLine(time, dic['SMA5'])
    chart1.drawLine(time, dic['SMA20'], color='green')
    chart1.drawLine(time, dic['SMA60'], color='blue')
    chart1.drawLine(time, dic['H2_SMA20'], color='yellow', linewidth=2.0)
    chart1.drawLine(time, dic['H4_SMA20'], color='orange', linewidth=2.0)
    chart1.drawLine(time, dic['BOLLINGER+'], color='gray', linewidth=0.5)
    chart1.drawLine(time, dic['BOLLINGER-'], color='gray', linewidth=0.5)
    chart1.drawMarkers(time, dic[const.LOW], -0.05, dic['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(time, dic[const.LOW], -0.05, dic['SIGNAL'], 2, '^', 'green', overlay=2, markersize=20)
    chart1.drawMarkers(time, dic[const.HIGH], 50, dic['SIGNAL'], -1, '^', 'red', overlay=1, markersize=20)
    chart1.drawMarkers(time, dic[const.HIGH], 50, dic['SIGNAL'], -2, '^', 'red', overlay=2, markersize=20)
    
    chart2 = CandleChart(fig, axes[1], comment='SLOPE')
    chart2.drawLine(time, dic['SLOPE_SMA5'], color='red')
    chart2.drawLine(time, dic['SLOPE_SMA60'], color='blue')
    chart2.drawLine(time, dic['SLOPE_SMA20'], color='green')
    chart2.drawLine(time, dic['SLOPE_SMA60'], color='blue')
    
    chart3 = CandleChart(fig, axes[2], comment='ATR')
    chart3.drawLine(time, dic['ATR'])
    
    chart4 = CandleChart(fig, axes[3], comment='ADX')
    chart4.drawLine(time, dic['ADX'])
    
    chart5 = CandleChart(fig, axes[4], comment='MA Trend', date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
    colors = {TA.UPPER_TREND: 'red',
              TA.UPPER_SUB_TREND: Colors.light_red,
              TA.UPPER_DIP: 'black',
              TA.LOWER_TREND: 'green',
              TA.LOWER_SUB_TREND: Colors.light_green,
              TA.LOWER_DIP: 'black',
              TA.NO_TREND: 'gray'}
    chart5.drawBand(time, dic['MA_TREND'], colors=colors, xlabel=True)

def displayChart(ticker, data: ResampleDataBuffer, years, months, from_hour, to_hour):
    time = data.dic[const.TIME]
    t0 = t1 = None
    for year in years:
        for month in months:
            for day in range(1, 32):
                try:
                    t0 = TimeUtils.pyTime(year, month, day, from_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
                    t1 = TimeUtils.pyTime(year, month, day, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
                    if to_hour < from_hour:
                        t1 += timedelta(days=1)                        
                except:
                    continue
                n, begin, end = TimeUtils.sliceTime(time, t0, t1)
                if n < 50:
                    continue
                dic = Utils.sliceDic(data.dic, begin, end)
                plotChart(ticker, dic)

def main():
    ticker = 'GBPJPY'
    click_sec = ClickSecData()
    data = click_sec.fxData(ticker, 2022, 10, 2023, 1, 5)
    dic = data.dic
    #print(dic['H4'][1000:1050])
    print(dic.keys())
    time = dic[const.TIME]
    print(time[0], '--', time[-1])
    displayChart(ticker, data, [2022], np.arange(1, 2), 7, 2)
       
if __name__ == '__main__':
    main()