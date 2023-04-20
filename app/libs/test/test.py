# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 07:47:06 2023

@author: IKU
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../MarketData'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import pandas as pd
from Converter import Converter
from MarketData import readFile, candles2tohlc, getCandles, str2time_fx
from const import const
from Utils import Utils
from TimeUtils import TimeUtils
from DataServerStub import DataServerStub
from DataBuffer import DataBuffer, ResampleDataBuffer


def test_resample1():
    files = ['../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220107.csv',
            '../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220110.csv']
    
    candles = getCandles(files, str2time_fx)
    tohlc = candles2tohlc(candles)
    #Utils.saveArrays('./gbpjpy_1min.csv', tohlc)


    tohlc2, data = Converter.resample(tohlc, 15, const.UNIT_MINUTE)
    Utils.saveArrays('./gbpjpy_15min.csv', tohlc2)    
    
    
def test_resample2():
    df = pd.read_csv('./gbpjpy_15min.csv', index_col=0)

    op = list(df.iloc[:, 0].values)
    hi = list(df.iloc[:, 1].values)
    lo = list(df.iloc[:, 2].values)
    cl = list(df.iloc[:, 3].values)
    time = TimeUtils.str2pytimeArray(list(df.index), TimeUtils.TIMEZONE_TOKYO)
    tohlc = [time, op, hi, lo, cl]
    tohlc2, _ = Converter.resample(tohlc, 2, const.UNIT_HOUR)
    Utils.saveArrays('./gbpjpy_2hours.csv', tohlc2)

def test():
    server = DataServerStub('DJI')
    server.importFile('../data/DJI_Feature_2019_08.csv')
    tohlcv_list = server.init(100, step_sec=10)
    #print(tohlcv_list)

    for i in range(10):
        [tohlcv1, tohlcv2] = server.nextData()
        print(tohlcv1)
        print(tohlcv2)
        print('.')

def saveCandles(filepath, candles):
    f = open(filepath, mode='w')
    f.write('Time, Open, High, Low, Close\n')
    for candle in candles:
        s = ''
        for value in candle:
            s += str(value) + ','
        f.write(s + '\n')
    f.close()
    
def test_databuffer1():
    files = ['../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220107.csv',
            '../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220110.csv']    
    candles = getCandles(files, str2time_fx)
    tohlc = candles2tohlc(candles)
    Utils.saveArrays('./gbpjpy_1min.csv', tohlc)    
    server = DataServerStub('DJI')
    server.importFile('./gbpjpy_1min.csv', TimeUtils.TIMEZONE_TOKYO)
    data = server.init(1430, step_sec=10)
    buffer = DataBuffer(data, [])
    while True:
        d = server.nextData()
        print(d)
        if d[0] is None:
            break
        buffer.update(d)
    candles = buffer.candles()
    print(candles[0])
    saveCandles('./buffered_gbpjpy_1min.csv', candles)
    
def test_databuffer2():
    files = ['../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220107.csv',
            '../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220110.csv']    
    candles = getCandles(files, str2time_fx)
    tohlc = candles2tohlc(candles)
    Utils.saveArrays('./test2/gbpjpy_1min.csv', tohlc)
    tohlc2, _ = Converter.resample(tohlc, 5, const.UNIT_MINUTE)
    Utils.saveArrays('./test2/gbpjpy_5min.csv', tohlc2)   

    server = DataServerStub('DJI')
    server.importFile('./test2/gbpjpy_1min.csv', TimeUtils.TIMEZONE_TOKYO)
    data = server.init(1430, step_sec=10)
    buffer = ResampleDataBuffer(data, [], 5)
    while True:
        d = server.nextData()
        print(d)
        if d[0] is None:
            break
        buffer.update(d)
    candles = buffer.candles()
    print(candles[0])
    saveCandles('./test2/buffered_gbpjpy_5min.csv', candles)
    
def test_databuffer3():
    files = ['../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220107.csv',
            '../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220110.csv']    
    candles = getCandles(files, str2time_fx)
    tohlc = candles2tohlc(candles)
    tohlc2, _ = Converter.resample(tohlc, 5, const.UNIT_MINUTE)
    Utils.saveArrays('./test3/gbpjpy_5min.csv', tohlc2)    
    server = DataServerStub('DJI')
    server.importFile('./test3/gbpjpy_5min.csv', TimeUtils.TIMEZONE_TOKYO)
    data = server.init(1430, step_sec=10)
    buffer = DataBuffer(data, [])
    while True:
        d = server.nextData()
        print(d)
        if d[0] is None:
            break
        buffer.update(d)
    candles = buffer.candles()
    print(candles[0])
    saveCandles('./test3/buffered_gbpjpy_5min.csv', candles)       
    
def test_databuffer4():
    files = ['../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220107.csv',
            '../../MarketData/GBPJPY/GBPJPY_202201/202201/GBPJPY_20220110.csv']    
    candles = getCandles(files, str2time_fx)
    tohlc = candles2tohlc(candles)
    tohlc2, _ = Converter.resample(tohlc, 4, const.UNIT_HOUR)
    Utils.saveArrays('./test4/gbpjpy_4hours.csv', tohlc2)   

    server = DataServerStub('DJI')
    server.importFile('./test2/gbpjpy_1min.csv', TimeUtils.TIMEZONE_TOKYO)
    data = server.init(1430, step_sec=10)
    buffer = ResampleDataBuffer(data, [], 4 * 60)
    while True:
        d = server.nextData()
        print(d)
        if d[0] is None:
            break
        buffer.update(d)
    candles = buffer.candles()
    print(candles[0])
    saveCandles('./test4/buffered_gbpjpy_4hours.csv', candles)    

if __name__ == '__main__':
    test_databuffer3()