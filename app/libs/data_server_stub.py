# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 16:26:45 2023

@author: IKU-Trader
"""
import os
import numpy as np
import polars as pl
from polars import DataFrame
import numpy as np
import glob
import pytz
from const import const
from time_utils import TimeUtils

def fileList(dir_path, extension):
    path = os.path.join(dir_path, '*.' + extension)
    l = glob.glob(path)
    return l

def sortIndex(array:[]):
    index = [pair[0] for pair in sorted(enumerate(array), key=lambda x:x[1])]
    return index
       
def sortWithIndex(array:[], index:[]):
    if len(array) != len(index):
        return None
    out = [array[i] for i in index]
    return out

# -----
    
class DataServerStub:
    def __init__(self, name:str):
        self.name = name
        pass
  
    def merge(self, tohlcv, new_tohlcv):
        if tohlcv is None:
            tohlcv = new_tohlcv
            return tohlcv
        for old, new in zip(tohlcv, new_tohlcv):
            old += new
        return tohlcv
    
    def parseTime(self, tohlcv:[], tzinfo):
        time = TimeUtils.str2pytimeArray(tohlcv[0], tzinfo)
        jst = TimeUtils.changeTimezone(time, TimeUtils.TIMEZONE_TOKYO)
        index = sortIndex(jst)        
        jst = sortWithIndex(jst, index)
        out = [jst]
        for i in range(1, len(tohlcv)):
            d = sortWithIndex(tohlcv[i], index)
            out.append(d)
        return out
    
    def importFiles(self, dir_path, tzinfo):
        tohlcv = None  
        for file in fileList(dir_path, 'csv'):
            df = pl.read_csv(file)
            data = self.toTohlcv(df)
            tohlcv = self.merge(tohlcv, data)
        tohlcv = self.parseTime(tohlcv, tzinfo)
        self.tohlcv = self.resample(tohlcv, self.interval, self.time_unit)
        
    def importFile(self, file_path, tzinfo):
        df = pl.read_csv(file_path)
        tohlcv = self.toTohlcv(df)
        tohlcv = self.parseTime(tohlcv, tzinfo)
        self.tohlcv = tohlcv
        
    def importData(self, tohlcv):
        self.tohlcv = tohlcv
        
    def init(self, initial_num:int, step_sec=0):
        if initial_num > self.size():
            raise Exception('Too large initial_num: ' + str(initial_num) + '  data size: ' + str(self.size()))
        self.currentIndex = initial_num - 1
        tohlcv = self.sliceTohlcv(0, self.currentIndex)
        if step_sec == 0:
            self.step_num = 0
        else:
            self.step_num = int(60 / step_sec) - 1
            self.dummy = self.makeDummy(self.tohlcvAt(self.currentIndex + 1), self.step_num)
        self.step = 0
        self.lastValidTohlcv = self.tohlcvAt(self.currentIndex)
        print('step sec:', step_sec, 'num:', self.step_num, 'step: ', self.step, 'len(dummy)', len(self.dummy))
        return tohlcv

    def makeDummy(self, next_tohlcv, num):
        t = next_tohlcv[0]
        lo = next_tohlcv[3]
        hi = next_tohlcv[2]
        
        prices = np.linspace(lo, hi, num)
        np.random.shuffle(prices)
        dummy = []
        o = next_tohlcv[1]
        h = o
        l = o
        if len(next_tohlcv) > 5:
            is_volume = True
            vo = next_tohlcv[5]
            dv = int(vo / num - 0.5)
        else:
            is_volume = False
        sumvol = 0
        for i, price in enumerate(prices):
            if i == 0:
                h = price
                l = price
            else:
                if price > h:
                    h = price
                if price < l:
                    l = price
            if is_volume:
                sumvol += dv
                if sumvol > vo:
                    v = vo - sumvol
                else:
                    v = dv
                dummy.append([t, o, h, l, price, v])
            else:
                dummy.append([t, o, h, l, price])
        return dummy
        
    def nextData(self):        
        print('next data ... step: ', self.step, 'len(dummy): ', len(self.dummy))
        if self.step_num == 0:
            self.currentIndex += 1
            if self.currentIndex > self.size() - 1:
                return [None, None]
            else:
                return [self.lastValidTohlcv, self.tohlcAt(self.currentIndex)]
        else:
            self.step += 1
            if self.step > self.step_num:
                self.step = 0
                self.currentIndex += 1
                if self.currentIndex < self.size() - 1:
                    self.dummy = self.makeDummy(self.tohlcvAt(self.currentIndex + 1), self.step_num)
                
                last = self.lastValidTohlcv.copy()
                current = self.tohlcvAt(self.currentIndex)
                self.lastValidTohlcv = current
                return [last, current]
            else:
                return [self.lastValidTohlcv, self.dummy[self.step - 1]] 

    def sliceTohlcv(self, begin: int, end: int):
        out = []
        for array in self.tohlcv:
            out.append(array[begin: end + 1])
        return out
    
    def tohlcvAt(self, index):
        if index < self.size():
            out = [values[index] for values in self.tohlcv]
            return out
        else:
            return None
        
    def indexAt(self, time):
        begin, end = self.timeRange()
        if time < begin and time > end:
            return -1
        for i, t in self.tohlcv[0]:
            if t >= time:
                return i
        
    def timeRange(self):
        t0 = self.tohlcv[0][0]
        t1 = self.tohlcv[0][-1]
        return (t0, t1)

    def size(self):
        return len(self.tohlcv[0])
    
    def getCandles(self, time_from=None, time_to=None):
        tohlcv = self.getTohlcv(time_from=time_from, time_to=time_to)
        if len(tohlcv) == 0:
            return []
        return self.toCandles(tohlcv)

    def toTohlcv(self, df: DataFrame):
        time = df[const.TIME].to_list()
        op = df[const.OPEN].to_numpy()
        hi = df[const.HIGH].to_numpy()
        lo = df[const.LOW].to_numpy()
        cl = df[const.CLOSE].to_numpy()
        out = [time, op, hi, lo, cl]
        if const.VOLUME in df.columns:
            out.append(df[const.VOLUME].to_numpy())
        return out