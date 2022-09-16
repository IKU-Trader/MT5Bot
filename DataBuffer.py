# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from const import *
from TechnicalAnalysis import atr, sma
from utility import dic2Arrays, sliceDic, dic2df

class DataBuffer:
    def __init__(self, features:list, calc_functions: dict):
        self.features = features
        self.calc_functions = calc_functions
        self.dic = None
        
    def slicedData(self, begin, end):
        return sliceDic(self.dic, begin, end)
    
    def minMax(self, begin, end):
        dic = self.slicedData(begin, end)
        high = dic[HIGH]
        low = dic[LOW]
        return (min(low), max(high))
    
    def data(self):
        return self.dic
    
    def size(self):
        if self.dic is None:
            return 0
        return len(self.dic[TIMEJST])
    
    def lastTime(self):
        if self.size() > 0:
            return self.dic[TIMEJST][-1]
        else:
            return None
        
    def deltaTime(self):
        if self.size() > 1:
            time = self.dic[TIMEJST]
            dt = time[1] - time[0]
            return dt
        else:
            return None
        
    def needSize(self):
        t1 = datetime.now(TIMEZONE_TOKYO)
        t0 = self.lastTime()
        n = (t1 - t0) / self.deltaTime()
        n = int(n + 0.5) +1
        return n
    
    def loadData(self, dic):
        self.dic = dic
        end = self.size() - 1
        self.calcFeatures(dic, 0, end)
        print(dic.keys())
        return   
    
    def deleteLastData(self, dic):
        keys, arrays = dic2Arrays(dic)
        out = {}
        for key, array in zip(keys, arrays):
            out[key] = array[:-1]
        return out
    
    def update(self, dic, should_delete_last=True):
        if should_delete_last:
            self.dic = self.deleteLastData(self.dic)
        keys, arrays = dic2Arrays(self.dic)
        keys, newarrays = dic2Arrays(dic)        
        last_time = self.dic[TIMESTAMP][-1]
        indices = []
        for i  in range(len(dic[TIMESTAMP])):
            t = dic[TIMESTAMP][i]
            if t > last_time:
                indices.append(i)
                last_time = t
                for array, newarray in zip(arrays, newarrays):
                    array.append(newarray[i])
        n = len(self.dic[TIMESTAMP])
        m = len(indices)
        begin = n - m
        end = n -1
        self.calcFeatures(self.dic, begin, end)
        return (begin, end)
    
    
    def calcFeatures(self, dic, begin, end):
        for key in self.features:
            f = self.calc_functions[key]
            ret = f(key, dic, begin, end)
            if not ret:
                print('Error in ', key)
        return True
        
def save(dic, filepath):
    keys = dic.keys()
    data = []
    keys, arrays = DataBuffer.dic2Arrays(dic)
    n = len(arrays[0])
    for i in range(n):
        d = []
        for array in arrays:
            d.append(array[i])
        data.append(d)
    df = pd.DataFrame(data=data, columns=keys)
    df.to_csv(filepath, index=False)
    
def test():
    pass

if __name__ == '__main__':
    test()
    #save('US30Cash', 'D1')


        
