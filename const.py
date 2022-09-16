# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 09:49:46 2022

@author: docs9
"""

from datetime import datetime, timedelta, timezone
import calendar
import pytz
import MetaTrader5 as mt5


GEM_FX = ['USDJPY', 'AUDJPY', 'GBPJPY', 'EURJPY', 'EURUSD', 'GBPUSD', 'GBPAUD' ]
GEM_INDEX = ['DOWUSD', 'NASUSD', 'S&PUSD', 'JPXJPY', 'DAXEUR', 'HSXHKD']
GEM_COMODITY = ['WTIUSD', 'XAUUSD', 'XAGUSD']
GEM = GEM_INDEX + GEM_COMODITY + GEM_FX


TIMEJST = 'timejst'
TIMESTAMP = 'timestamp'
OPEN = 'open'
HIGH = 'high'
LOW = 'low'
CLOSE = 'close'
VOLUME = 'volume'

    
UNIT_MINUTE = 'MINUTE'
UNIT_HOUR = 'HOUR'
UNIT_DAY = 'DAY'

TIMEZONE_TOKYO = timezone(timedelta(hours=+9), 'Asia/Tokyo')

             # symbol : [(mt5 timeframe constants), number, unit]
TIMEFRAME = {'M1': [mt5.TIMEFRAME_M1,  1, UNIT_MINUTE],
             'M5': [mt5.TIMEFRAME_M5,  5, UNIT_MINUTE],
             'M10': [mt5.TIMEFRAME_M10, 10, UNIT_MINUTE],
             'M15': [mt5.TIMEFRAME_M15, 15, UNIT_MINUTE],
             'M30': [mt5.TIMEFRAME_M30, 30, UNIT_MINUTE],
             'H1': [mt5.TIMEFRAME_H1  ,  1, UNIT_HOUR],
             'H4': [mt5.TIMEFRAME_H4,    4, UNIT_HOUR],
             'H8': [mt5.TIMEFRAME_H8,    8, UNIT_HOUR],
             'D1': [mt5.TIMEFRAME_D1,    1, UNIT_DAY]}

LONG = 1
SHORT = -1

ATR = 'atr'
TR = 'tr'
SMA = 'sma'
HL2 = 'hl2'
ATR_BAND_UPPER = 'atr_band_upper'
ATR_BAND_LOWER = 'atr_band_lower'
ATR_BREAKUP_SIGNAL = 'atr_breakup_signal'
ATR_BREAKDOWN_SIGNAL = 'atr_breakdown_signal'

WINDOW = 'window'
COEFF = 'coeff'



