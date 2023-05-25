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
from libs.data_buffer import ResampleDataBuffer
from market_data import MT5Data
from libs.candle_chart import CandleChart, BandPlot, makeFig, gridFig, Colors
from libs.technical_analysis import TA
from libs.converter import Converter
from libs.const import const


def prepare_data_for_model_input(prices, ma):
    '''
        Input:
        prices (df) - Dataframe of close prices
        ma (int) - legth of the moveing average
        
        Output:
        prices(df) - An enhanced prices dataframe, with moving averages and log return columns
        prices_array(nd.array) - an array of log returns
    '''
    
    intrument = prices.columns.name
    prices[f'{intrument}_ma'] = prices.rolling(ma).mean()
    prices[f'{intrument}_log_return'] = np.log(prices[f'{intrument}_ma']/prices[f'{intrument}_ma'].shift(1)).dropna()
 
    prices.dropna(inplace = True)
    prices_array = np.array([[q] for q in prices[f'{intrument}_log_return'].values])
    
    return prices, prices_array

def load_data(ticker, timeframe):
    mt5 = MT5Data('../market_data/mt5/gemforex/' + timeframe)
    df = mt5.importFromCsv(ticker, timeframe)
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    return df
    


def main():
    df = load_data('DOWUSD', 'D1')
    prices, prices_array = prepare_data_for_model_input(df[[const.TIME, const.CLOSE]], 16)
       
    pass
if __name__ == '__main__':
    main()

