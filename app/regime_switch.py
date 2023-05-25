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


def preprocess(df, ma_window):
    df['price'] = df[const.CLOSE]
    df= df.with_columns(df['price'].rolling_mean(ma_window).alias('ma'))
    log_return = np.log(df['price'] / df['price'].shift(1))
    df.with_columns(pl.Series(name='log_return', values=log_return))
    df.dropna(inplace = True)
    return df['log_return'].to_numpy()

def load_data(ticker, timeframe):
    mt5 = MT5Data('../market_data/mt5/gemforex/' + timeframe)
    df = mt5.importFromCsv(ticker, timeframe)
    print('data size:', len(df))
    time = df[const.TIME]
    print(time[0], '-->', time[-1])
    return df
    


def main():
    df = load_data('DOWUSD', 'D1')
    prices = preprocess(df, 16)
       
    pass
if __name__ == '__main__':
    main()

