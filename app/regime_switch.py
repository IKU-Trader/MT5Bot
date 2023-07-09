# -*- coding: utf-8 -*-
"""
Created on Thu May 25 15:31:39 2023

@author: IKU-Trader
"""

import os
import sys

import polars as pl
from polars import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

from hmmlearn.hmm import GaussianHMM
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
import math


from libs.utils import Utils
from libs.time_utils import TimeUtils
from market_data import MT5Data
from libs.candle_chart import CandleChart, BandPlot, makeFig, gridFig, Colors
from libs.technical_analysis import TA
from libs.converter import Converter
from libs.const import const

class RegimeDetector:
 
    def get_regimes_hmm(self, input_data, params):
        hmm_model = self.initialise_model(GaussianHMM(), params).fit(input_data)
        return hmm_model
    
    def get_regimes_clustering(self, params):
        clustering =  self.initialise_model(AgglomerativeClustering(), params)
        return clustering
    
    def get_regimes_gmm(self, input_data, params):
        gmm = self.initialise_model(GaussianMixture(), params).fit(input_data)
        return gmm
        
    def initialise_model(self, model, params):
        for parameter, value in params.items():
            setattr(model, parameter, value)
        return model
    
    
def create_hmm_model(log_returns):
    model = GaussianHMM(n_components=2, covariance_type="full", n_iter=1000)
    model.fit(log_returns)
    print("Model Score:", model.score(log_returns))
    return model

def spike(df):
    op = df[const.OPEN]
    hi = df[const.HIGH]
    lo = df[const.LOW]
    cl = df[const.CLOSE]
    upper = []
    lower = []
    for o, h, l, c in zip(op, hi, lo, cl):
        if c > o:
            upper.append(h - c)
            lower.append(o - l)
        else:
            upper.append(h - o)
            lower.append(c - l)
    return upper, lower

def preprocess(df, ma_window):
    df = df.with_columns(df[const.CLOSE].alias('price'))
    df = df.with_columns(df['price'].rolling_mean(ma_window).alias('ma'))
    log_return = np.log(df['price'] / df['price'].shift(1))
    df = df.with_columns(pl.Series(name='log_return', values=log_return))
    hl = df[const.HIGH] / df[const.LOW] - 1
    df = df.with_columns(pl.Series(name='HL', values=hl))
    upper, lower = spike(df)
    df = df.with_columns(pl.Series(name='spike+', values=upper))
    df = df.with_columns(pl.Series(name='spike-', values=lower))
    df = df.drop_nulls()
    #array = df[['log_return', 'spike+', 'spike-']].to_numpy()
    array = df[['log_return']].to_numpy()
    array = array.reshape(-1, 1)
    return df, array

def load_data(ticker, timeframe):
    mt5 = MT5Data('../market_data/mt5/xm/' + timeframe)
    df = mt5.importFromCsv(ticker, timeframe)
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    return df
    
def plot_hidden_states(title, df, clustering_states):
    fig, ax = makeFig(1, 1, (15, 5))
    chart = CandleChart(fig, ax, title=title, date_format=CandleChart.DATE_FORMAT_YEAR_MONTH)
    states = set(clustering_states)
    colors = ['red', 'blue', 'green', 'orange', 'yellow', 'brown', 'violet']
    price = df['price']
    time = df[const.TIME]
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
        
def plot_hidden_states_daily(df, clustering_states, from_hour, to_hour):
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
            title = str(t)
            plot_hidden_states(title, df[begin: end + 1], clustering_states[begin: end + 1])
        t += timedelta(days=1)
    
    
def print_term(label, df: DataFrame):
    time = df[const.TIME]
    print(label + ' Date ', time[0], '～', time[-1])
    
def main0():
    df = load_data('GBPJPY', 'M1')
    n = len(df)
    m = int(n / 2)
    train = df[m:, :]
    test = df[m:, :]
    
    train, train_prices = preprocess(train, 7)
    detector = RegimeDetector()
    params = {'n_clusters': 3, 'linkage': 'complete',  'metric': 'manhattan', 'random_state':100}
    clustering = detector.get_regimes_clustering(params)
    clustering_states = clustering.fit_predict(train_prices)
    plot_hidden_states(train, clustering_states)

def main(brand, timeframe, train_rate, plot_daily=False):
    df = load_data(brand, timeframe)
    n = len(df)
    m = int(n * train_rate)
    train = df[:m, :]
    print_term('Train ', train)
    test = df[m:, :]
    print_term('Test ', test)
    
    train, train_features = preprocess(train, 7)
    test, test_features = preprocess(test, 7)
    model = create_hmm_model(train_features)
    states = model.predict(test_features)
    if plot_daily:
        plot_hidden_states_daily(test, states, 11, 5) 
    else:
        plot_hidden_states(brand + '-' + timeframe, test, states)     
    
if __name__ == '__main__':
    market = 'GBPAUD'
    timeframes = ['M5'] #, 'M5', 'M1']
    rates = [0.90] #, 0.8, 0.8]
    for timeframe, rate in zip(timeframes, rates):
        main(market, timeframe, rate, True)

