# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 17:44:54 2023

@author: IKU-Trader
"""

import polars as pl
from polars import DataFrame
from datetime import datetime, timedelta
from .const import const
from .time_utils import TimeUtils


class Converter:
    @staticmethod
    def candles2tohlc(candles):
        is_volume = (len(candles[0]) > 5)
        times = []
        op = []
        hi = []
        lo = []
        cl = []
        vol = []
        for candle in candles:
            times.append(candle[0])
            op.append(candle[1])
            hi.append(candle[2])
            lo.append(candle[3])
            cl.append(candle[4])
            if is_volume:
                vol.append(candle[5])
        if is_volume:
            return [times, op, hi, lo, cl, vol]
        else:
            return [times, op, hi, lo, cl]
    
    @staticmethod
    def df2Candles(df: DataFrame):
        df2 = df[[const.OPEN, const.HIGH, const.LOW, const.CLOSE]]
        return df2.to_list()
    
    @staticmethod
    def df2dic(df: DataFrame) ->dict:
        t = df[const.TIME].to_list()
        o = df[const.OPEN].to_numpy()
        h = df[const.HIGH].to_numpy()
        l = df[const.LOW].to_numpy()
        c = df[const.CLOSE].to_numpy()
        dic = {const.TIME: t, const.OPEN: o, const.HIGH: h, const.LOW: l, const.CLOSE: c}
        if const.VOLUME in df.columns:
            v = df[const.VOLUME].to_numpy()
            dic[const.VOUME] = v
        return dic
    
    @staticmethod
    def df2tohlcv(df: DataFrame) ->dict:
        t = df[const.TIME].to_list()
        o = df[const.OPEN].to_numpy()
        h = df[const.HIGH].to_numpy()
        l = df[const.LOW].to_numpy()
        c = df[const.CLOSE].to_numpy()
        tohlcv = [t,  o, h, l, c]
        if const.VOLUME in df.columns:
            v = df[const.VOLUME].to_numpy()
            tohlcv.append(v)
        return tohlcv
    
    @staticmethod
    def tohlcv2Candles(tohlcv):
        op = tohlcv[1]
        hi = tohlcv[2]
        lo = tohlcv[3]
        cl = tohlcv[4]
        candles = []
        for o, h, l, c in zip(op, hi, lo, cl):
            candles.append([o, h, l, c])
        return candles
    
    @staticmethod
    def tohlcvArrays2dic(tohlcv: list, is_last_invalid):
        dic = {}
        if is_last_invalid:
            dic[const.TIME] = tohlcv[0][:-1]
            dic[const.OPEN] = tohlcv[1][:-1]
            dic[const.HIGH] = tohlcv[2][:-1]
            dic[const.LOW] = tohlcv[3][:-1]
            dic[const.CLOSE] = tohlcv[4][:-1]
            if len(tohlcv) > 5:
                dic[const.VOLUME] = tohlcv[5][:-1]
            candle = [tohlcv[0][-1], tohlcv[1][-1], tohlcv[2][-1],tohlcv[3][-1], tohlcv[4][-1]]
            if len(tohlcv) > 5:
                candle.append(tohlcv[5][-1])
            return dic, candle
        else:
            dic = Converter.arrays2Dic(tohlcv)
            return dic, []

    @staticmethod        
    def dic2Arrays(dic: dict):
        arrays = [dic[const.TIME], dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE]]
        if const.VOLUME in dic.keys():
            arrays.append(dic[const.VOLUME])
        return arrays 
    
    @staticmethod        
    def arrays2Dic(tohlcvArrays: list):
        dic = {}
        dic[const.TIME] = tohlcvArrays[0]
        dic[const.OPEN] = tohlcvArrays[1]
        dic[const.HIGH] = tohlcvArrays[2]
        dic[const.LOW] = tohlcvArrays[3]
        dic[const.CLOSE] = tohlcvArrays[4]
        if len(tohlcvArrays) > 5:
            dic[const.VOLUME] = tohlcvArrays[5]
        return dic    
    
    @staticmethod
    def arrays2Candles(tohlcvArrays: list):
        out = []
        n = len(tohlcvArrays[0])
        for i in range(n):
            d = [array[i] for array in tohlcvArrays]
            out.append(d)
        return out

    @staticmethod
    def candles2dic(candles: list):
        n = len(candles)
        m = len(candles[0])
        arrays = []
        for i in range(m):
            array = [candles[j][i] for j in range(n)]
            arrays.append(array)
            
        dic = {const.TIME: arrays[0], const.OPEN: arrays[1], const.HIGH: arrays[2], const.LOW: arrays[3], const.CLOSE: arrays[4]}
        if m > 5:
            dic[const.VOLUME] = arrays[5]
        return dic

    @staticmethod
    def dic2Candles(dic: dict):
        arrays = [dic[const.TIME], dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE]]
        try:
            arrays.append(dic[const.VOLUME])
        except:
            pass
        out = []
        for i in range(len(arrays[0])):
            d = [] 
            for array in arrays:
                d.append(array[i])
            out.append(d)
        return out
    
    # tohlcv: tohlcv arrays
    @staticmethod
    def resample(dic: dict, interval: int, unit: const.TimeUnit):        
        time = dic[const.TIME]
        n = len(time)
        op = dic[const.OPEN]
        hi = dic[const.HIGH]
        lo = dic[const.LOW]
        cl = dic[const.CLOSE]
        if const.VOLUME in dic.keys():
            vo = dic[const.VOLUME]
            is_volume = True
        else:
            is_volume = False
        tmp_candles = []
        candles = []
        for i in range(n):
            if is_volume:
                values = [time[i], op[i], hi[i], lo[i], cl[i], vo[i]]
            else:
                values = [time[i], op[i], hi[i], lo[i], cl[i]]
            t_round = Converter.roundTime(time[i], interval, unit)
            if time[i] == t_round:
                tmp_candles.append(values)
                candle = Converter.candlePrice(time[i], tmp_candles)
                candles.append(candle)
                tmp_candles = []
            elif time[i] < t_round:
                tmp_candles.append(values)
            elif time[i] > t_round:
                tmp_candles = []
        return Converter.candles2dic(candles), candles, tmp_candles
    
    @staticmethod
    def roundTime(time: datetime, interval: int, unit: const.TimeUnit):
        zone = time.tzinfo
        if unit == const.UNIT_MINUTE:
            t = datetime(time.year, time.month, time.day, time.hour, 0, 0, tzinfo=zone)
        elif unit == const.UNIT_HOUR:
            t = datetime(time.year, time.month, time.day, 0, 0, 0, tzinfo=zone)
        elif unit == const.UNIT_DAY:
            if TimeUtils.isSummerTime(time):
                hour = 6
            else:
                hour = 7
            if time.hour <= hour:    
                return datetime(time.year, time.month, time.day, hour, 0, 0, tzinfo=zone)
            else:
                t = datetime(time.year, time.month, time.day, hour, 0, 0, tzinfo=zone)
                t += timedelta(days=1)
                return t
                
        if t == time:
            return t
        while t < time:
            if unit == const.UNIT_MINUTE:
                t += timedelta(minutes=interval)
            elif unit == const.UNIT_HOUR:
                t += timedelta(hours=interval)
        return t

    @staticmethod
    def candlePrice(time:datetime, tohlcv_list:[]):
        m = len(tohlcv_list[0])
        n = len(tohlcv_list)
        o = tohlcv_list[0][1]
        c = tohlcv_list[-1][4]
        h_array = [tohlcv_list[i][2] for i in range(n)]
        h = max(h_array)
        l_array = [tohlcv_list[i][3] for i in range(n)]
        l = min(l_array)
        if m > 5:
            v_array = [tohlcv_list[i][5] for i in range(n)]
            v = sum(v_array)
            return [time, o, h, l, c, v]
        else:
            return [time, o, h, l, c]    