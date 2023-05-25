# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 15:35:02 2023

@author: IKU
"""

import os
import numpy as np
import polars as pl
from polars import DataFrame
from datetime import datetime

from libs.utils import Utils
from libs.time_utils import TimeUtils
from libs.data_buffer import ResampleDataBuffer
from libs.const import const
from libs.converter import Converter

def currentPath():
    return os.path.dirname(os.path.abspath(__file__))

def absPath(relative_path):
    return os.path.join(currentPath(), relative_path)
    
# ------
    
class ClickSecData:
    def __init__(self):
        self.home_dir = '../market_data/cick_sec'
        self.tickers = ['GBPAUD', 'GBPJPY', 'gold']
        
    def readFile(self, path, str2time):
        f = open(path, encoding='sjis')
        line = f.readline()
        line = f.readline()
        tohlc = []
        while line:
            values = line.split(',')
            s = values[0]
            t = str2time(s) 
            o = float(values[1])
            h = float(values[2])
            l = float(values[3])
            c = float(values[4])
            tohlc.append([t, o, h, l, c])
            line = f.readline()
        f.close()
        return tohlc
    
    def str2timeGold(self, s: str):
        return TimeUtils.pyTime(int(s[0:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]), int(s[10:12]), 0, TimeUtils.TIMEZONE_TOKYO)

    def str2timeFx(self, s: str):
        form = '%Y/%m/%d %H:%M:%S'
        t = datetime.strptime(s, form)
        t = t.astimezone(TimeUtils.TIMEZONE_TOKYO)
        return t
    
    def getCandles(self, files, str2time_func):
        tohlc = []
        for file in files:
           d = self.readFile(file, str2time_func)
           tohlc += d     
        candles = sorted(tohlc, key=lambda s: s[0])
        return candles
    
    def goldData(self, years, months, interval_minutes):
        dir_path = absPath(self.home_dir + '/gold')
        files = []
        for year in years:
            for m in months:
                path = os.path.join(dir_path, str(year) + str(m).zfill(2))
                if os.path.exists(path):
                    l = Utils.fileList(path, '*.csv')
                    if len(l) > 0:
                        files += l
        candles = self.getCandles(files, self.str2timeGold)
        tohlc = Converter.candles2tohlc(candles)
        return candles, tohlc
    
    def fxData(self, symbol, from_year, from_month, to_year, to_month, interval_minutes):
        dir_path = absPath(self.home_dir + '/' + symbol)
        files = []
        year  = from_year
        month = from_month
        while True:
            path = os.path.join(dir_path, symbol + '_' + str(year) + str(month).zfill(2))
            path = os.path.join(path, str(year) + str(month).zfill(2))
            if os.path.exists(path):
                l = Utils.fileList(path, '*.csv')
                if len(l) > 0:
                    files += l
            if year == to_year and month == to_month:
                break        
            month += 1
            if month > 12:
                year += 1
                month = 1
        candles = self.getCandles(files, self.str2timeFx)
        tohlc = Converter.candles2tohlc(candles)
        return candles, tohlc
    
class MT5Data:
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.tickers = ['GBPJPY']
        
    def importFromCsv(self, ticker_symbol: str, timeframe: str):
        file_list = Utils.fileList(self.home_dir, '*.csv')       
        for path in file_list:
            dir_path, filename = os.path.split(path)
            if filename.find(ticker_symbol) >= 0 and filename.find(timeframe) >= 0:
                df = pl.read_csv(path, separator='\t')
                if timeframe.lower() == 'd1':
                    return self.parse_day(df)
                else:
                    return self.parse(df)
            
    def parse(self, df):
        time_str = df['<DATE>'] + ' ' + df['<TIME>']
        time = TimeUtils.str2pytimeArray(time_str, form='%Y.%m.%d %H:%M:%S', timezone_str='+0900')
        d = {const.TIME: time, const.OPEN: df["<OPEN>"], const.HIGH: df["<HIGH>"], const.LOW: df['<LOW>'], const.CLOSE: df['<CLOSE>']}
        out = pl.DataFrame(d)
        print(out.head())
        return out
        
    def parse_day(self, df):
        time_str = df['<DATE>']
        time = TimeUtils.str2pytimeArray(time_str, form='%Y.%m.%d', timezone_str='+0900')
        d = {const.TIME: time, const.OPEN: df["<OPEN>"], const.HIGH: df["<HIGH>"], const.LOW: df['<LOW>'], const.CLOSE: df['<CLOSE>']}
        out = pl.DataFrame(d)
        print(out.head())
        return out    
    
if __name__ == '__main__':
    mt5_data = MT5Data()
    df = mt5_data.importFromCsv('GBPJPY', 'M5')