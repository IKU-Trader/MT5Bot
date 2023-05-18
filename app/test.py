# -*- coding: utf-8 -*-
"""
Created on Thu May 18 18:59:47 2023

@author: docs9
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
from libs.data_server_stub import DataServerStub




def test():
    ticker = 'GBPJPY'
    mt5 = MT5Data(r'..\market_data\mt5\gemforex\M1')
    df = mt5.importFromCsv('GBPJPY', 'M1')
    print('Data size:', len(df))
    server = DataServerStub('')
    server.importDf(df)
    tohlcv = server.init(5000, step_sec=10)
    
    ta_params = TA.full_kit()
    buffer = ResampleDataBuffer(tohlcv, ta_params, 5)

    for i in range(10):
        current, tmp = server.nextData()
        if current is None:
            break
        print(current)
        print(tmp)
       
if __name__ == '__main__':
    test()