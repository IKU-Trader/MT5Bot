# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:37:16 2022

@author: IKU-Trader
"""

import os
import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from .const import const
from .time_utils import TimeUtils

from .utils import Utils
from .converter import Converter
from .technical_analysis import TA
from .math_array import MathArray
    
# -----

class DataBuffer:
    # tohlcv: arrays ( time array, open array, ...)
    def __init__(self, tohlcv: list, ta_params: list, is_last_invalid=True):
        self.ta_params = ta_params
        dic, candle = Converter.tohlcvArrays2dic(tohlcv, is_last_invalid)        
        self.addIndicators(dic)
        self.dic = dic
        self.invalid_candle = candle
                                
    def tohlcvDic(self):
        return self.dic
    
    def candles(self):
        return Converter.dic2Candles(self.dic)
    
    def tohlcvArrays(self):
        return Utils.dic2Arrays(self.dic)
    
    def size(self):
        return len(self.dic[const.TIME])
    
    def lastTime(self):
        if self.size() > 0:
            return self.dic[const.TIME][-1]
        else:
            return None
        
    def deltaTime(self):
        if self.size() > 1:
            time = self.dic[const.TIME]
            dt = time[1] - time[0]
            return dt
        else:
            return None
       
    # dic: tohlcv+ array dict
    def addIndicators(self, dic: dict):
        for ta_param in self.ta_params:
            method, param, name = ta_param
            TA.indicator(dic, method, param, name=name)
        return dic

    def updateSeqIndicator(self, dic: dict, begin: int, end: int):
        for ta_param in self.ta_params:
            method, param, name = ta_param
            TA.indicator(dic, method, param, name=name)
            TA.seqIndicator(dic, method, begin, end, param, name=name)
        return dic
    # dic: tohlcv+ array dict
    def removeLastData(self, dic):
        keys, arrays = Utils.dic2Arrays(dic)
        out = {}
        for key, array in zip(keys, arrays):
            out[key] = array[:-1]
        return out
    
    # candles: tohlcv array
    def update(self, candles: list, is_last_invalid=True):
        if is_last_invalid:
            valid_candles = candles[:-1]
            self.invalid_candle = candles[-1]
        else:
            valid_candles = candles
            self.invalid_candle = None
        
        last_time = self.lastTime()
        new_candles = []
        for candle in valid_candles:
            if candle[0] > last_time:
                new_candles.append(candle)
        m = len(new_candles)
        if m > 0:
            begin = len(self.dic[const.TIME])        
            end = begin + m - 1
            self.merge(self.dic, new_candles)
            self.updateSeqIndicator(self.dic, begin, end)
           
    def temporary(self):
        if self.invalid_candle is None:
            return self.dic[const.TIME][-1], self.dic.copy()
        tmp_dic = copy.deepcopy(self.dic)
        self.merge(tmp_dic, [self.invalid_candle])        
        begin = len(tmp_dic[const.TIME]) - 1        
        end = begin
        self.updateSeqIndicator(tmp_dic, begin, end)
        return self.invalid_candle[0], tmp_dic

    def merge(self, dic: dict, candles: list):
        index = {const.TIME: 0, const.OPEN: 1, const.HIGH: 2, const.LOW: 3, const.CLOSE: 4, const.VOLUME: 5}
        n = len(candles)
        blank = MathArray.full(n, np.nan)
        for key, array in dic.items():
            try:
                i = index[key]
                a = [candle[i] for candle in candles]
                array += a
            except:
                array += blank.copy()
        return
            
# -----

class ResampleDataBuffer(DataBuffer):
    # tohlcv: arrays ( time array, open array, ...)
    def __init__(self, tohlcv: list, ta_params: list, interval_minutes: int):
        if interval_minutes > 60:
            raise Exception('Bad interval_minutes')
        tohlcv_arrays, tmp_candles = Converter.resample(tohlcv, interval_minutes, const.UNIT_MINUTE)
        super().__init__(tohlcv_arrays, ta_params, False)
        self.interval_minutes = interval_minutes
        self.tmp_candles = tmp_candles
            
    # candles: tohlcv array
    def update(self, candles):
        self.invalid_candle = candles[-1]
        valid_candles = candles[:-1]
        new_candles, tmp_candles = self.compositCandle(valid_candles)
        self.tmp_candles = tmp_candles
        m = len(new_candles)
        if m > 0:
            begin = len(self.dic[const.TIME])        
            end = begin + m - 1
            self.merge(self.dic, new_candles)
            self.updateSeqIndicator(self.dic, begin, end)
    
    def compositCandle(self, candles):
        tmp_candles = self.tmp_candles.copy()
        new_candles = []
        last_time = self.dic[const.TIME][-1]
        for candle  in candles:
            t = candle[0]
            if t <= last_time:
                continue
            t_round =  Converter.roundTime(t, self.interval_minutes, const.UNIT_MINUTE)
            if t == t_round:    
                tmp_candles.append(candle)
                c = Converter.candlePrice(t_round, tmp_candles)
                new_candles.append(c)
                tmp_candles = []
            else:
                if len(tmp_candles) > 0:
                    if t > tmp_candles[-1][0]:
                        tmp_candles.append(candle)
                else:
                    tmp_candles.append(candle)
        return new_candles, tmp_candles
        
    def temporary(self):
        tmp_candles = copy.deepcopy(self.tmp_candles)
        if self.invalid_candle is not None:
            tmp_candles.append(self.invalid_candle)
        if len(tmp_candles) == 0:
            return self.dic[const.TIME][-1], self.dic.copy()
        t = tmp_candles[-1][0]
        t_round =  Converter.roundTime(t, self.interval_minutes, const.UNIT_MINUTE)
        new_candle = Converter.candlePrice(t_round, tmp_candles)
        tmp_dic = copy.deepcopy(self.dic)
        begin = len(tmp_dic[const.TIME])
        self.merge(tmp_dic, [new_candle])        
        end = len(tmp_dic[const.TIME]) - 1
        self.updateSeqIndicator(tmp_dic, begin, end)
        return tmp_candles[-1][0], tmp_dic
