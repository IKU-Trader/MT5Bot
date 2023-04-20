# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:25:30 2022

@author: IKU-Trader
"""


from datetime import datetime, timedelta, timezone
import calendar
import pytz
import MetaTrader5 as mt5

class mt5_const:

    GEM_FX = ['USDJPY', 'AUDJPY', 'GBPJPY', 'EURJPY', 'EURUSD', 'GBPUSD', 'GBPAUD' ]
    GEM_INDEX = ['DOWUSD', 'NASUSD', 'S&PUSD', 'JPXJPY', 'DAXEUR', 'HSXHKD']
    GEM_COMODITY = ['WTIUSD', 'XAUUSD', 'XAGUSD']
    GEM = GEM_INDEX + GEM_COMODITY + GEM_FX
    
    TIMESTAMP = 'timestamp'
        
    UNIT_MINUTE = 'MINUTE'
    UNIT_HOUR = 'HOUR'
    UNIT_DAY = 'DAY'
    
    
    # MT5 timeframe
    M1 = 'M1'
    M5 = 'M5'
    M10 = 'M10'
    M15 = 'M15'
    M30 = 'M30'
    H1 = 'H1'
    H4 = 'H4'
    H8 = 'H8'
    D1 = 'D1'
                 # symbol : [(mt5 timeframe constants), number, unit]
    TIMEFRAME = {M1: [mt5.TIMEFRAME_M1,  1, UNIT_MINUTE],
                 M5: [mt5.TIMEFRAME_M5,  5, UNIT_MINUTE],
                 M10: [mt5.TIMEFRAME_M10, 10, UNIT_MINUTE],
                 M15: [mt5.TIMEFRAME_M15, 15, UNIT_MINUTE],
                 M30: [mt5.TIMEFRAME_M30, 30, UNIT_MINUTE],
                 H1: [mt5.TIMEFRAME_H1  ,  1, UNIT_HOUR],
                 H4: [mt5.TIMEFRAME_H4,    4, UNIT_HOUR],
                 H8: [mt5.TIMEFRAME_H8,    8, UNIT_HOUR],
                 D1: [mt5.TIMEFRAME_D1,    1, UNIT_DAY]}
    




