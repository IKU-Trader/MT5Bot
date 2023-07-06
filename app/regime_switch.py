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
    
def preprocess(df, ma_window):
    df = df.with_columns(df[const.CLOSE].alias('price'))
    df = df.with_columns(df['price'].rolling_mean(ma_window).alias('ma'))
    log_return = np.log(df['price'] / df['price'].shift(1))
    df = df.with_columns(pl.Series(name='log_return', values=log_return))
    df = df.drop_nulls()
    array = df['log_return'].to_numpy()
    array = array.reshape(-1, 1)
    return df, array

def load_data(ticker, timeframe):
    mt5 = MT5Data('../market_data/mt5/gemforex/' + timeframe)
    df = mt5.importFromCsv(ticker, timeframe)
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    return df
    
def plot_hidden_states(df, clustering_states):
    fig, ax = makeFig(1, 1, (12, 8))
    chart = CandleChart(fig, ax)
    states = set(clustering_states)
    colors = ['red', 'blue', 'green', 'orange', 'yellow', 'brown', 'violet']
    price = df['price']
    time = df[const.TIME]
    for i, state in enumerate(states):
        c = colors[i]
        array = []
        for p, s in zip(price, clustering_states):
            if s == state:
                array.append(p)
            else:
                array.append(np.nan)
        chart.drawLine(time, array, color=c)
    

def main():
    df = load_data('DOWUSD', 'D1')
    n = len(df)
    df = df[:int(n / 4), :]
    
    df, prices = preprocess(df, 7)
    detector = RegimeDetector()
    params = {'n_clusters': 2, 'linkage': 'complete',  'metric': 'manhattan', 'random_state':100}
    clustering = detector.get_regimes_clustering(params)
    clustering_states = clustering.fit_predict(prices)
    plot_hidden_states(df, clustering_states)

       
    pass
if __name__ == '__main__':
    main()

