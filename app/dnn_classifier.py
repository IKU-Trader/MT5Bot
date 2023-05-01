# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 21:58:04 2023

@author: IKU-Trader
"""
import numpy as np
import polars as pl
from polars import DataFrame
import matplotlib.pyplot as plt

import tensorflow as tf
from sklearn.preprocessing import StandardScaler
#from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation

from market_data import MT5Data
from libs.const import const

FEATURES = []

def split(df: DataFrame, rate=0.8):
    n = int(len(df) * rate)
    df_train = df[:n, :]
    df_test = df[n:, :]
    return df_train, df_test
    
def make_features(df: DataFrame, lags=5, should_dropna=True):
    data = DataFrame({const.TIME: df[const.TIME], 'price': df[const.CLOSE]})
    ret = np.log(data['price'] / data['price'].shift(1))
    direction = np.where(ret > 0, 1, 0)
    data = data.with_columns(pl.Series(name='return', values=ret))
    data = data.with_columns(pl.Series(name='direction', values=direction))    
    features = []
    for lag in range(lags):
        name = 'lag_' + str(lag)
        data = data.with_columns(data['return'].shift(lag).alias(name))
        features.append(name)
    data = data.with_columns(data['return'].rolling_mean(5).shift(1).alias('momentum'))
    data = data.with_columns(data['return'].rolling_std(5).shift(1).alias('volatility'))
    data = data.with_columns( (data['price'] - data['price'].rolling_mean(50).shift(1)).alias('distance'))
    if should_dropna:
        data = data.drop_nulls()
    features += ['momentum', 'volatility', 'distance']
    objective = 'direction'
    return (data, features, objective)
    
def create_scaler(df: DataFrame, features):
    scaler = StandardScaler()
    scaler.fit(df[features])
    return scaler
    
def create_model(input_dim: int):
    optimizer = Adam(learning_rate=0.0001)
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(input_dim,)))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer=optimizer, 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])  
    print(model.summary())
    return model

def learn(model, scaler, data: DataFrame, features, objective):
    train_x = scaler.transform(data[features])
    model.fit(x=train_x,
              y=np.array(data[objective]),
              epochs=50,
              verbose=True,
              validation_split=0.2,
              shuffle=False)
    
def evaluate(ticker, model, scaler, df: DataFrame, features, objective):
    scaled_x = scaler.transform(df[features])
    predicted = model.predict(scaled_x)
    plt.scatter(df[objective], predicted)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.show()
    
    
    prediction = np.where(predicted > 0, 1, -1)
    df = df.with_columns(pl.Series(name='prediction', values=prediction))
    profit = df['prediction'].to_numpy() * df['return'].to_numpy()
    df = df.with_columns(pl.Series(name='profit', values=profit))
    n = len(df)
    
    plt.plot(df[const.TIME], df['price'])
    plt.show()
    
    plt.plot(df[const.TIME], df['profit'])
    plt.show()
    
    
    #df['price'].plot(figsize=(10, 6))
    #df[['return', 'profit']].cumsum().apply(np.exp).plot(figsize=(10, 6), title=ticker)
    
    
def main(ticker):
    mt5_data = MT5Data()
    df = mt5_data.importFromCsv(ticker, 'M5')
    df_train, df_test = split(df)
    (df_train, features, objective) = make_features(df_train)
    (df_test, features, objective) = make_features(df_test)
    
    tf.random.set_seed(100)
    model = create_model(len(features))
    
    scaler = create_scaler(df_train, features)
    learn(model, scaler, df_train, features, objective)
    evaluate(ticker, model, scaler, df_test, features, objective)

    pass

if __name__ == '__main__':
    main('GBPAUD')
    #main('JPXJPY')
    #main('NASUSD')
    #main('XAUUSD')