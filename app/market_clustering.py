# -*- coding: utf-8 -*-
"""
Created on Mon May  8 08:39:24 2023

@author: docs9

see.: https://github.com/oreilly-japan/artificial-intelligence-with-python-ja/blob/master/Chapter%204/stocks.ipynb
"""

from datetime import datetime 
import json 
import numpy as np 
from sklearn import covariance, cluster 
import polars as pl
from yahoo_finance_api2 import share as api

from libs.yahoo_finance_api import YahooFinanceApi, TIMEZONE_NY

TIMEFRAME = 'D1'
input_file = './company_symbol_mapping.json'


def to_numpy(mat: list):
    rows = len(mat)
    cols = len(mat[0])
    array = np.full((rows, cols), np.nan)
    error_rows = []
    for r in range(rows):
        v = mat[r]
        if len(v) != cols:
            print('Col size is bad  row:' + str(r))
            error_rows.append(r)
            continue
        for c in range(cols):
            if np.isnan(v[c]):
                print('Nan error row: ' + str(r) + ' col:' + str(c))
                error_rows.append(r)
                break
            array[r, c] = v[c]
    return array, error_rows

def remove_cols(matrix, cols):
    out = []
    for i, line in enumerate(matrix):
        if not i in cols:
            out.append(line)
    return out
    
def analyze():
    with open(input_file, 'r') as f:
        symbols_map = json.loads(f.read())
        
    symbols = symbols_map.keys()
    print(symbols)
        
    t0 = datetime(2003, 7,3)
    t1 = datetime(2007, 5,4)

    quotes = []
    names = []

    param = [api.PERIOD_TYPE_WEEK, 40, api.FREQUENCY_TYPE_DAY, 1]
    for symbol in symbols:
        try:
            df = YahooFinanceApi.download(symbol, param, TIMEZONE_NY)
            if df is not None:
                dif = df['close']- df['open']
                quotes.append(dif.to_list())
                names.append(symbol)
                print('Found', symbol, len(df))
        except:
            print('Not found', symbol)
            
    #names = np.array(names)
        
    x, error_rows = to_numpy(quotes)
    if len(error_rows) > 0:
        quotes = remove_cols(quotes, error_rows)
        names = remove_cols(names, error_rows)
        x, error_rows = to_numpy(quotes)
        if len(error_rows) > 0:
            return
    
    print('market num:', len(names))
    print('x shape:', x.shape)
    
    x = x.T
    x /= x.std(axis=0)

    model = covariance.GraphicalLassoCV(cv=3)

    with np.errstate(invalid='ignore'):
        model.fit(x)
        
    _, labels = cluster.affinity_propagation(model.covariance_)
    num_labels = labels.max()
    print('labels num: ', len(labels))

    names = np.array(names)
    for i in range(num_labels + 1):
        print('Cluster', i + 1, '==>', ', '.join(names[labels == i]))
    
    
if __name__ == '__main__':
    analyze()
