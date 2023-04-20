# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 14:32:19 2022

@author: IKU-Trader
"""

import numpy as np

class MathArray(object):
    
    @classmethod 
    def full(cls, length: int, value):
        out = [value for i in range(length)]
        return out
    
    @classmethod
    def addArray(cls, array1: list, array2: list) ->list:
        out = []
        for a1, a2 in zip(array1, array2):
            if np.isnan(a1) or np.isnan(a2):
                out.append(np.nan)
            else:
                out.append(a1 + a2)
        return out
    
    @classmethod
    def subtractArray(cls, array1: list, array2: list) ->list:
        out = []
        for a1, a2 in zip(array1, array2):
            if np.isnan(a1) or np.isnan(a2):
                out.append(np.nan)
            else:
                out.append(a1 - a2)
        return out
        
    @classmethod
    def multiply(cls, array: list, value: float) ->list:
        out = []
        for a in array:
            if np.isnan(a) :
                out.append(np.nan)
            else:
                out.append(value * a)
        return out   
        
        
    @classmethod
    def greater(cls, ref:list, array:list) -> list:
        out = []
        for r, a in zip(ref, array):
            if np.isnan(r) or np.isnan(a):
                out.append(0)
            else:
                if r < a:
                    out.append(1)
                else:
                    out.append(0)
        return out
    
    @classmethod
    def greaterEqual(cls, ref: list, array:list) -> list:
        out = []
        for r, a in zip(ref, array):
            if np.isnan(r) or np.isnan(a):
                out.append(0)
            else:
                if r <= a:
                    out.append(1)
                else:
                    out.append(0)
        return out

    @classmethod    
    def smaller(cls, ref: list, array:list) -> list:
        out = []
        for r, a in zip(ref, array):
            if np.isnan(r) or np.isnan(a):
                out.append(0)
            else:
                if r > a:
                    out.append(1)
                else:
                    out.append(0)
        return out
    
    @classmethod
    def smallerEqual(cls, ref: list, array: list) -> list:
        out = []
        for r, a in zip(ref, array):
            if np.isnan(r) or np.isnan(a):
                out.append(0)
            else:
                if r >= a:
                    out.append(1)
                else:
                    out.append(0)
        return out