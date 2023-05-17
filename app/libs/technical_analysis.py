# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 18:19:54 2023

@author: IKU-Trader
"""

import os
import numpy as np
import polars as pl
from polars import DataFrame
import math
from .utils import Utils
from .math_array import MathArray
from .const import const
from .data_buffer import Converter
from .time_utils import TimeUtils

def nans(length):
    return [np.nan for _ in range(length)]

def arrays2dic(tohlcv:[]):
    dic = {}
    dic[const.TIME] = tohlcv[0]
    dic[const.OPEN] = tohlcv[1]
    dic[const.HIGH] = tohlcv[2]
    dic[const.LOW] = tohlcv[3]
    dic[const.CLOSE] = tohlcv[4]
    if len(tohlcv) > 5:
        dic[const.VOLUME] = tohlcv[5]
    return dic
    
class TA:
    # ----- constants
    TAMethod = str
    ATR: TAMethod = 'atr'
    TR: TAMethod = 'tr'
    SMA: TAMethod = 'sma'
    HL2: TAMethod = 'hl2'
    DIplus: TAMethod = 'diplus'
    DIminus: TAMethod = 'diminus'
    DX: TAMethod = 'dx'
    ADX: TAMethod = 'adx'
    SLOPE: TAMethod = 'slope'
    
    BOLLINGER_BAND_UPPER: TAMethod = 'bollinger_band_upper'
    BOLLINGER_BAND_LOWER: TAMethod = 'bollinger_band_lower'
    
    ATR_BAND_UPPER: TAMethod = 'atr_band_upper'
    ATR_BAND_LOWER: TAMethod = 'atr_band_lower'
    ATR_BREAKUP_SIGNAL: TAMethod = 'atr_breakup_signal'
    ATR_BREAKDOWN_SIGNAL: TAMethod = 'atr_breakdown_signal'

    MA_TREND_BAND: TAMethod = 'ma_trend_band'
    PATTERN_MATCH: TAMethod = 'pattern_match'
    
    UPPER_TIMEFRAME: TAMethod = 'upper_timeframe'
    
    # ----- parameter keys

    TAParam = str
    WINDOW: TAParam = 'window'
    COEFF: TAParam = 'coeff'
    SIGMA: TAParam = 'sigma'

    # MA Trend
    THRESHOLD: TAParam = 'threshold'
    MA_KEYS: TAParam  = 'ma_keys'
    NO_TREND = 0
    UPPER_TREND = 1
    UPPER_SUB_TREND = 2
    UPPER_DIP =  3
    LOWER_TREND = -1
    LOWER_SUB_TREND = -2
    LOWER_DIP = -3

    SOURCE: TAParam = 'source'
    PATTERNS: TAParam = 'patterns'
    TIMEFRAME: TAParam = 'timeframe'
    # -----    
 
    @staticmethod
    def basic_kit():
        params = [
                    [TA.SMA, {TA.WINDOW: 5}, 'SMA5'],
                    [TA.SMA, {TA.WINDOW: 20}, 'SMA20'],
                    [TA.SMA, {TA.WINDOW: 60}, 'SMA60'],
                ]
        return params
    
    @staticmethod
    def full_kit():
        trend_params = {TA.MA_KEYS:['SMA5', 'SMA20', 'SMA60'], TA.THRESHOLD:0.05}
        patterns = {
                        TA.SOURCE: 'MA_TREND',
                        TA.PATTERNS:[
                                [[TA.NO_TREND, TA.UPPER_TREND], 1, 0],
                                [[TA.UPPER_SUB_TREND, TA.UPPER_TREND], 1, 0],
                                [[TA.NO_TREND, TA.LOWER_TREND], 2, 0],
                                [[TA.LOWER_SUB_TREND, TA.LOWER_TREND], 2, 0]
                                ]
                    }

        params = [
                    [TA.SMA, {TA.WINDOW: 5}, 'SMA5'],
                    [TA.SMA, {TA.WINDOW: 20}, 'SMA20'],
                    [TA.SMA, {TA.WINDOW: 60}, 'SMA60'],
                    [TA.ATR, {TA.WINDOW: 14}, 'ATR'],
                    [TA.ADX, {TA.WINDOW: 14}, 'ADX'],
                    [TA.BOLLINGER_BAND_UPPER, {TA.WINDOW: 14, TA.SIGMA: 2.0}, 'BOLLINGER+'],
                    [TA.BOLLINGER_BAND_LOWER, {TA.WINDOW: 14, TA.SIGMA: 2.0}, 'BOLLINGER-'],
                    [TA.SLOPE, {TA.SOURCE: 'SMA5', TA.WINDOW: 3}, 'SLOPE_SMA5'],
                    [TA.SLOPE, {TA.SOURCE: 'SMA20', TA.WINDOW: 3}, 'SLOPE_SMA20'],
                    [TA.SLOPE, {TA.SOURCE: 'SMA60', TA.WINDOW: 3}, 'SLOPE_SMA60'],
                    [TA.MA_TREND_BAND, trend_params, 'MA_TREND'],
                    [TA.PATTERN_MATCH, patterns, 'SIGNAL'],
                    [TA.UPPER_TIMEFRAME, {TA.SOURCE: const.CLOSE, TA.TIMEFRAME: 'H2', TA.WINDOW: 20}, 'H2_SMA20'],
                    [TA.UPPER_TIMEFRAME, {TA.SOURCE: const.CLOSE, TA.TIMEFRAME: 'H4', TA.WINDOW: 20}, 'H4_SMA20'],
                    [TA.UPPER_TIMEFRAME, {TA.SOURCE: const.CLOSE, TA.TIMEFRAME: 'D1', TA.WINDOW: 5}, 'D1_SMA5']
                ]
        return params
    
    
    #------
    
    @staticmethod 
    def candleBody(open_price,  high_price, low_price, close_price):
        body_low = min([high_price, low_price])
        body_high = max([high_price, low_price])
        body = body_high - body_low
        is_positive = close_price > open_price
        spike_high = high_price - body_high
        spike_low = body_low - low_price
        return (is_positive, body, body_low, body_high)
    
    @staticmethod
    def candleSpike(open_price, high_price, low_price, close_price):
        is_positive, body, body_low, body_high = TA.candleBodey(open_price, high_price, low_price, close_price)
        spike_high = high_price - body_high
        spike_low = body_low - low_price
        return (spike_high, spike_low)

    @staticmethod
    def hl2(dic):
        hi = dic[const.HIGH]
        lo = dic[const.LOW]
        out = MathArray.addArray(hi, lo)
        out = MathArray.multiply(out, 0.5)
        return out
    
    @staticmethod
    def sma(array, window):
        n = len(array)
        out = nans(n)
        for i in range(window - 1, n):
            s = 0.0
            count = 0
            for j in range(window):
                a = array[i - j]
                if np.isnan(a):
                    continue
                else:
                    count += 1
                    s += a
            if count > 0:                
                out[i] = s / count
        return out            

    @staticmethod         
    def tr(hi, lo, cl):
        n = len(cl)
        out = nans(n)
        out[0] = hi[0] - lo[0]
        for i in range(1, n):
            r1 = np.abs(hi[i] - lo[i])
            r2 = np.abs(hi[i] - cl[i - 1])
            r3 = np.abs(cl[i - 1] - lo[i])
            out[i] = np.max([r1, r2, r3])
        return out
       
    @staticmethod
    def atr(hi, lo, cl, window):
        trdata = TA.tr(hi, lo, cl)
        out = TA.sma(trdata, window)
        return (out, trdata)
    
    @staticmethod
    def di(hi, lo, cl, window):
        n = len(hi)
        dmp = nans(n)
        dmn = nans(n)
        for i in range(1, n):
            dmp[i] = hi[i] - hi[i - 1]
            dmn[i] = lo[i - 1] - lo[i]
        dmplus = nans(n)
        dmminus = nans(n)
        for i in range(1, n):
            if dmp[i] < 0 and dmn[i] < 0:
                dmplus[i] = 0
                dmminus[i] = 0
            elif dmp[i] > dmn[i]:
                dmplus[i] = dmp[i]
                dmminus[i] = 0
            elif dmp[i] < dmn[i]:
                dmplus[i] = 0
                dmminus[i] = dmn[i]
            elif dmp[i] == dmn[i]:
                dmplus[i] = 0
                dmminus[i] = 0
            elif dmp[i] < 0 and dmn[i] < 0:
                dmplus[i] = 0
                dmminus[i] = 0   
        diplus = nans(n)
        diminus = nans(n)
        tr = TA.tr(hi, lo, cl)
        for i in range(window, n):
            diplus[i] = 100.0 * sum(dmplus[i - window + 1 : i + 1]) / sum(tr[i - window  + 1: i + 1])
            diminus[i] = 100.0 * sum(dmminus[i - window + 1: i + 1]) / sum(tr[i - window + 1: i + 1])
        return (dmplus, dmminus, diplus, diminus)
    
    @staticmethod
    def adx(hi, lo, cl, window):
        (dmplus, dmminus, diplus, diminus) = TA.di(hi, lo, cl, window)
        n = len(diplus)
        dx = nans(n)
        for i in range(1, n):
            dx[i] = 100.0 * abs(diplus[i] - diminus[i]) / (diplus[i] + diminus[i])        
        adx = nans(n)
        for i in range(window * 2 - 1, n):
            adx[i] = sum(dx[i - window + 1: i + 1]) / float(window)
        return adx
    
    @staticmethod 
    def slope(array: list, window: int):
        data = np.array(array)
        n = len(array)
        out = nans(n)
        x = np.arange(0, window)
        for i in range(window - 1, n):            
            y = data[i - window + 1: i + 1]
            m, offset = np.polyfit(x, y, 1)        
            out[i] = 100.0 * m / data[i - window + 1]
        return out
    
    @staticmethod
    def mean(array):
        s = 0.0
        count = 0
        for a in array:
            if a is None:
                continue
            if np.isnan(a):
                continue
            s += a
            count += 1
        if count == 0:
            return (np.nan, count)
        else:
            return (s / float(count), count)
        
    @staticmethod
    def stdev(array):
        mean, count = TA.mean(array)
        if count == 0:
            return np.nan
        s = 0.0
        for a in array:
            if a is None:
                continue
            if np.isnan(a):
                continue
            s += (a - mean) * (a - mean)
        variance = s / float(count)
        std = math.sqrt(variance)
        return std
        
    @staticmethod
    def bolingerBand(array: list, window: int, sigma: float):    
        sma = TA.sma(array, window)
        n = len(array)
        upper = nans(n)
        lower = nans(n)
        for i in range(window - 1, n):
            mean = sma[i]
            std = TA.stdev(array[i - window + 1: i + 1])
            if np.isnan(mean) == False and np.isnan(std) == False:
                upper[i] = mean + std * sigma
                lower[i] = mean - std * sigma                
        return (upper, lower)                
    
    @staticmethod
    def atrBand(cl: list, atr: list, k: float):
        m =  MathArray.multiply(atr, k)
        upper = MathArray.addArray(cl, m)
        lower = MathArray.subtractArray(cl, m)
        return (upper, lower)
    
    @staticmethod
    def breakSignal(op: list, cl: list, level: float, is_up: bool, offset: int=1):
        if offset < 0:
            return None
        n = len(cl)
        signal = []
        for i in range(n):
            if i < offset:
                signal.append(0)
                continue
            if is_up:
                p = max(op[i], cl[i])
                t = p > level[i - offset]
            else:
                p = min(op[i], cl[i])
                t = p < level[i - offset]
            if t:
                signal.append(1)
            else:
                signal.append(0)
        return signal
    
    @staticmethod
    def maTrendBand(op: list, hi: list, lo: list, cl: list, ma_list: list, threshold: float):
        w1 = MathArray.subtractArray(ma_list[0], ma_list[1])
        w2 = MathArray.subtractArray(ma_list[1], ma_list[2])
        n = len(w1)
        out = MathArray.full(n, TA.NO_TREND)
        for i in range(n):
            if w1[i] > 0 and w2[i] > 0:
                out[i] = TA.UPPER_TREND
            elif w1[i] > 0 and w2[i] < 0:
                out[i] = TA.UPPER_SUB_TREND
            elif w1[i] < 0 and w2[i] < 0:
                out[i] = TA.LOWER_TREND
            elif w1[i] < 0 and w2[i] > 0:
                out[i] = TA.LOWER_SUB_TREND
            if out[i] == TA.UPPER_TREND:
                (is_positive, body, body_low, body_high) = TA.candleBody(op[i], hi[i], lo[i], cl[i])
                if ma_list[1][i] > body_low:
                    out[i] = TA.UPPER_DIP
            if out[i] == TA.LOWER_TREND:
                (is_positive, body, body_low, body_high) = TA.candleBody(op[i], hi[i], lo[i], cl[i])
                if ma_list[1][i] < body_high:
                    out[i] = TA.LOWER_DIP            
            if abs(w1[i] / ma_list[1][i] * 100.0) < threshold and abs(w2[i] / ma_list[2][i] * 100.0 < threshold):
                out[i] = TA.NO_TREND
        return out
    
    @staticmethod
    def patternMatching(signal: list, patterns: list):
        n = len(signal)
        out = MathArray.full(n, np.nan)
        for [pattern, value, offset] in patterns:
            m = len(pattern)
            for i in range(n - m):
                if signal[i: i + m] == pattern:
                    out[i + m  - 1 + offset] = value
        return out

    @staticmethod
    def upperTimeframe(dic: dict, refkey: str, time_symbol: str, ma_window: int=0):
        time = dic[const.TIME]
        #arrays = [time, dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE]]
        value, unit = const.timeSymbol2elements(time_symbol)
        tohlcv_dic, candles, tmp_candles = Converter.resample(dic, value, unit)    
        sample_time = tohlcv_dic[const.TIME]
        sample_data = tohlcv_dic[refkey]
        if ma_window > 0:
            sample_data = TA.sma(sample_data, ma_window)
        data = nans(len(time))
        #Utils.saveArrays('./sampled.csv', [sample_time, sample_data])
        current = np.nan
        i = 0
        for j in range(len(time)):
            if time[j] >= sample_time[i]:
                if time[j] == sample_time[i]:
                    current = sample_data[i]
                else:
                    if not np.isnan(current):
                        current = np.nan
                i += 1
                if i >= len(sample_data):
                    break
            data[j] = current
        return data
    
# -----
    
    @staticmethod 
    def seqIndicator(dic: dict, key: str, begin: int, end:int, params: dict, name:str=None):
        if name is None:
            name = key
        n = len(dic[const.OPEN])
        if TA.WINDOW in params.keys():
            window = params[TA.WINDOW]
        else:
            window = 0
        if not name in dic.keys():
            data = dic
            begin = 0
            end = n - 1
        else:
            if window > 0:
                if begin < window:
                    data = dic
                else:
                    data = Utils.sliceDic(dic, begin - window, end)
            else:
                data = Utils.sliceDic(dic, begin, end)
        array = TA.indicator(data, key, params, name=name, should_set=False)    
        if array is None:
            return False
        original = dic[name]
        if name in dic.keys():
            j = len(array) - (end - begin + 1)
            original[begin: end + 1] = array[j:]
        else:
            original[name] = array
        return True
    
    @staticmethod
    def indicator(data: dict, key:str, params:dict, name:str=None, should_set=True):
        op = data[const.OPEN]
        hi = data[const.HIGH]
        lo = data[const.LOW]
        cl = data[const.CLOSE]
        
        # common parameter
        if TA.WINDOW in params.keys():
            window = params[TA.WINDOW]
        if TA.COEFF in params.keys():
            coeff = params[TA.COEFF]
            
        # technical analysis
        if key == TA.SMA:
            array = TA.sma(cl, window)
        elif key == TA.ATR:
            array, _ = TA.atr(hi, lo, cl, window)
        elif key == TA.ADX:
            array = TA.adx(hi, lo, cl, window)
        elif key == TA.SLOPE:
            source = params[TA.SOURCE]
            signal = data[source]
            array = TA.slope(signal, window)
        elif key == TA.BOLLINGER_BAND_UPPER:
            sigma = params[TA.SIGMA]
            array, _ = TA.bolingerBand(cl, window, sigma)
        elif key == TA.BOLLINGER_BAND_LOWER:
            sigma = params[TA.SIGMA]
            _, array = TA.bolingerBand(cl, window, sigma)             
        elif key == TA.ATR_BAND_UPPER or key == TA.ATR_BAND_LOWER:
            atr = data[TA.ATR]
            upper, lower = TA.atrBand(cl, atr, coeff)
            if key == TA.ATR_BAND_UPPER:
                array = upper
            else:
                array = lower
        elif key == TA.ATR_BREAKUP_SIGNAL:
            level = data[TA.ATR_BAND_UPPER]
            array = TA.breakSignal(data, level, True)
        elif key == TA.ATR_BREAKDOWN_SIGNAL:
            level = TA.ATR_BAND_LOWER
            array = TA.breakSignal(op, cl, level, False)
        elif key == TA.MA_TREND_BAND:
            threshold = params[TA.THRESHOLD]
            ma_keys = params[TA.MA_KEYS]
            mas = [data[key] for key in ma_keys]
            if len(mas) != 3:
                raise Exception('Bad MA_TREND_BAND parameter')
            array = TA.maTrendBand(op, hi, lo, cl, mas, threshold)
        elif key == TA.PATTERN_MATCH:
            source = params[TA.SOURCE]
            signal = data[source]
            patterns = params[TA.PATTERNS]
            array = TA.patternMatching(signal, patterns)
        elif key == TA.UPPER_TIMEFRAME:
            source = params[TA.SOURCE]
            timeframe = params[TA.TIMEFRAME]
            array = TA.upperTimeframe(data, source, timeframe, ma_window=window)
        else:
            return None
        
        if name is None:
            name = key
        if should_set:
            data[name] = array
        return array
    
    @staticmethod
    def isKeys(dic, keys):
        for key in keys:
            if not key in dic.keys():
                return False
        return True