# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 21:58:04 2023

@author: IKU-Trader
"""
import numpy as np
import pandas as pd

#from tensorflow import keras
#from keras.models import Model, Sequential
#from keras.layers import Dense, Activation, Conv2D, MaxPooling2D, Flatten

from market_data import MT5Data
from libs.const import const

def split(data: np.array):
    rate = 0.8
    n = int(len(data) * rate)
    train_data = data[:n]
    test_data = data[n:]
    return train_data, test_data
    
def make_features(df: pd.DataFrame, lags=5):
    data = pd.DataFrame({'price': df[const.CLOSE]})
    data[const.TIME] = df.index   
    data['return'] = np.log(data['price'] / data['price'].shift(1))
    data['direction'] = np.where(data['return'] > 0, 1, 0)
    for lag in range(lags):
        name = 'lag_' + str(lag)
        data[name] = data['return'].shift(lag)
    data['momentum'] = data['return'].rolling(5).mean().shift(1)
    data['volatility'] = data['return'].rolling(5).std().shift(1)
    data['distance'] = (data['price'] - data['price'].rolling(50).mean()).shift(1)
    return data
    

def main():
    mt5_data = MT5Data()
    df = mt5_data.importFromCsv('GBPJPY', 'M5')
    data = make_features(df)
    
    pass


if __name__ == '__main__':
    main()
