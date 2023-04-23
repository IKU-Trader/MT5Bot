# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 22:24:47 2023

@author: IKU-Trader
"""

class const:
    TIME = 'time'
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    
    TimeUnit = str
    UNIT_MINUTE:TimeUnit = 'MINUTE'
    UNIT_HOUR:TimeUnit = 'HOUR'
    UNIT_DAY:TimeUnit = 'DAY'
    
    @staticmethod
    def timeSymbol2elements(symbol: str):
        u = symbol[0].upper()
        unit = None
        if u == 'D':
            unit = const.UNIT_DAY
        elif u == 'H':
            unit = const.UNIT_HOUR
        elif u == 'M':
            unit = const.UNIT_MINUTE
        else:
            raise Exception('Bad time unit symbol ...'  + symbol)
            
        try:
            n = int(symbol[1:])
            return (n, unit)            
        except:
            raise Exception('Bad time unit symbol ...'  + symbol)