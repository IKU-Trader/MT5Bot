# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 10:04:17 2023

@author: docs9
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sklearn.mixture as mix
from pandas_datareader.data import DataReader
import polars as pl
from polars import DataFrame
import matplotlib.pyplot as plt

import yfinance as yf
# Machine Learning
from hmmlearn.hmm import GaussianHMM

from libs.const import const
from libs.utils import Utils
from libs.time_utils import TimeUtils
from libs.candle_chart import CandleChart, BandPlot, makeFig, gridFig, Colors
from market_data import MT5Data

LOG_RETURN = 'log_return'
RANGE = 'range'
FEATURES = [LOG_RETURN, RANGE]

def split(df: DataFrame, train_rate):
    n = len(df)
    m = int(n * train_rate)
    df_train = df[:m, :]
    df_test = df[m:, :]
    return df_train, df_test
    
def load_yahoo_data(symbol):
    start_date = "2017-01-1"
    end_date = "2023-07-01"
    data = yf.download(symbol, start=start_date, end=end_date)
    d = {const.TIME: data.index.values,
         const.OPEN: data["Open"].values,
         const.HIGH: data["High"].values,
         const.LOW: data['Low'].values,
         const.CLOSE: data['Close'].values,
         const.VOLUME: data['Volume'].values}
    df = pl.DataFrame(d)    
    return df

def load_data(ticker, timeframe):
    mt5 = MT5Data('../market_data/mt5/xm/' + timeframe)
    df = mt5.importFromCsv(ticker, timeframe)
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    return df
    
def create_features(df: DataFrame):
    log_return = np.log(df[const.CLOSE] / df[const.CLOSE].shift(1))
    df = df.with_columns(pl.Series(name=LOG_RETURN, values=log_return))
    hl = df[const.HIGH] / df[const.LOW] - 1
    df = df.with_columns(pl.Series(name=RANGE, values=hl))
    df = df.drop_nulls()
    return df
    
def create_hmm_model(x_train: DataFrame, classes: int):
    while True:
        try:
            hmm_model = GaussianHMM(n_components=classes, covariance_type="full", n_iter=100).fit(x_train)
            print("Model Score:", hmm_model.score(x_train))
            return hmm_model
        except:
            continue
    return None

def predict(model, x_test):
    states = model.predict(x_test)
    unique = set(states)
    print('States: ', unique)
    dic = {}
    for i, s in enumerate(set(states)):
        dic[s] = i
    out = []
    for s in states:
        out.append(dic[s])
    print('States2: ', set(out))
    return out
    
def plot_hidden_states(title, df, clustering_states, draw_candles=False, date_format=CandleChart.DATE_FORMAT_YEAR_MONTH):
    fig, ax = makeFig(1, 1, (20, 5))
    chart = CandleChart(fig, ax, title=title, date_format=date_format)
    states = set(clustering_states)
    colors = ['red', 'blue', 'orange', 'brown', 'yellow', 'black']
    price = df[const.CLOSE]
    time = df[const.TIME]
    if draw_candles:
        chart.drawCandle(time, df[const.OPEN], df[const.HIGH], df[const.LOW], df[const.CLOSE])
    for i, state in enumerate(states):
        c = colors[i]
        array = []
        for p, s in zip(price, clustering_states):
            if s == state:
                array.append(p)
            else:
                array.append(np.nan)
        chart.drawLine(time, array, color=c, xlabel=True)

def plot_hidden_states_daily(title, df, clustering_states, from_hour, to_hour):
    time = df[const.TIME]
    t = time[0]
    tfrom = TimeUtils.pyTime(t.year, t.month, t.day, from_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    tto = TimeUtils.pyTime(t.year, t.month, t.day, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    if tto < tfrom:
        tto += timedelta(days=1)
    if tfrom < time[0]:
        tfrom += timedelta(days=1)
    t = tfrom
    while t < time[-1]:
        t1 = TimeUtils.pyTime(t.year, t.month, t.day, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
        if t1 < t:
            t1 += timedelta(days=1)
        (n, begin, end) = TimeUtils.sliceTime(time, t, t1)
        if n > 20:
            label = title + '  ' + str(t)
            plot_hidden_states(label, df[begin: end + 1], clustering_states[begin: end + 1], draw_candles=True, date_format='%Y-%m-%d /%H')
        t += timedelta(days=1)
        
def plot_hidden_states_weekly(title, df, clustering_states):
    time = df[const.TIME]
    t = time[0]
    t = TimeUtils.pyTime(t.year, t.month, t.day, 0, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    w = t.weekday()
    if t != 1:
        days = (7 + 6 - w) % 7
        t += timedelta(days=days)        
    while t < time[-1]:
        t1 =  t + timedelta(days=6)
        (n, begin, end) = TimeUtils.sliceTime(time, t, t1)
        if n > 20:
            label = title + '  ' + str(t)
            plot_hidden_states(label, df[begin: end + 1], clustering_states[begin: end + 1], draw_candles=True, date_format=CandleChart.DATE_FORMAT_DAY)
        t += timedelta(days=7)        
        
                
def fill_with(time, time_ref, value_ref):
    n = len(time)
    value = np.full(n, np.nan)
    current = 0
    for t, v in zip(time_ref, value_ref):
        for i in range(current, n):
            if time[i] == t:
                value[i] = v
                current = i + 1 
                break
    # interpolate
    for i in range(1, n):
        if np.isnan(value[i]):
            value[i] = value[i - 1]
    return value

def test1():
    symbol = 'MSFT'
    df = load_yahoo_data(symbol)
    df = create_features(df)
    df_train, df_test = split(df, 0.5)
    x_train = df_train[FEATURES]
    x_test = df_test[FEATURES]
    model = create_hmm_model(x_train, 2)
    states = predict(model, x_test)
    plot_hidden_states(symbol, df_test, states)
    
def slice_time(df: DataFrame, time_from: datetime, time_to: datetime):
    time = df[const.TIME]
    n, begin, end = TimeUtils.sliceTime(time, time_from, time_to)
    out = df[begin: end + 1]
    return out
        
def test2():
    symbol = 'US30Cash'
    df = load_data(symbol, 'H4')
    t0 = TimeUtils.pyTime(2017, 1, 1, 0, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    t1 = TimeUtils.pyTime(2023, 7, 1, 0, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    #df = slice_time(df, t0, t1)
    df = create_features(df)
    df_train, df_test = split(df, 0.98)
    x_train = df_train[FEATURES]
    x_test = df_test[FEATURES]
    model = create_hmm_model(x_train, 2)
    states = predict(model, x_test)
    #plot_hidden_states(symbol, df_test, states, draw_candles=True)
    plot_hidden_states_weekly(symbol, df_test, states)
        
if __name__ == '__main__':
    test2()
    
    
    
    
    
    