# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 21:58:04 2023

@author: IKU-Trader
"""
import numpy as np
import pandas as pd
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

def split(df: pd.DataFrame, rate=0.8):
    n = int(len(df) * rate)
    df_train = df.iloc[:n, :]
    df_test = df.iloc[n:, :]
    return df_train, df_test
    
def make_features(df: pd.DataFrame, lags=5, should_dropna=True):
    data = pd.DataFrame({'price': df[const.CLOSE]})
    data[const.TIME] = df.index   
    data['return'] = np.log(data['price'] / data['price'].shift(1))
    data['direction'] = np.where(data['return'] > 0, 1, 0)
    features = []
    for lag in range(lags):
        name = 'lag_' + str(lag)
        data[name] = data['return'].shift(lag)
        features.append(name)
    data['momentum'] = data['return'].rolling(5).mean().shift(1)
    data['volatility'] = data['return'].rolling(5).std().shift(1)
    data['distance'] = (data['price'] - data['price'].rolling(50).mean()).shift(1)
    if should_dropna:
        data = data.dropna()
    features += ['momentum', 'volatility', 'distance']
    objective = 'direction'
    return (data, features, objective)
    
def create_scaler(df: pd.DataFrame, features):
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

def learn(model, scaler, data: pd.DataFrame, features, objective):
    train_x = scaler.transform(data[features])
    model.fit(x=train_x,
              y=np.array(data[objective].values),
              epochs=50,
              verbose=True,
              validation_split=0.2,
              shuffle=False)
    
def evaluate(model, scaler, data: pd.DataFrame, features, objective):
    scaled_x = scaler.transform(data[features])
    predicted = model.predict(scaled_x)    
    plt.scatter(data[objective], predicted)
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    
def main():
    mt5_data = MT5Data()
    df = mt5_data.importFromCsv('GBPJPY', 'M5')
    df_train, df_test = split(df)
    (df_train, features, objective) = make_features(df_train)
    (df_test, features, objective) = make_features(df_test)
    
    tf.random.set_seed(100)
    model = create_model(len(features))
    
    scaler = create_scaler(df_train, features)
    learn(model, scaler, df_train, features, objective)
    evaluate(model, scaler, df_test, features, objective)

    pass

if __name__ == '__main__':
    main()