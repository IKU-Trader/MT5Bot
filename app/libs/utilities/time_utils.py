# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 22:37:16 2022

@author: IKU-Trader
"""

import calendar
import pytz
from datetime import datetime, timezone, timedelta

class TimeUtils:

    TIMEZONE_TOKYO = pytz.timezone('Asia/Tokyo')

    @staticmethod
    def changeTimezone(pytime_array: list, tzinfo):
        out =[]
        for i in range(len(pytime_array)):
            t = pytime_array[i].astimezone(tzinfo)
            out.append(t)
        return out
       
    @staticmethod
    def str2pytimeArray(time_str_array: list, tzinfo, form='%Y-%m-%d %H:%M:%S'):
        out = []
        for s in time_str_array:
            i = s.find('+')
            if i > 0:
                s = s[:i]
            t = datetime.strptime(s, form)
            t = TimeUtils.pyTime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo)
            out.append(t)
        return out
    
    @staticmethod
    def str2pytime(time_str: str, tzinfo, form='%Y-%m-%d %H:%M:%S'):
        i = time_str.find('+')
        if i > 0:
            s = time_str[:i]
        else:
            s = time_str
        t = datetime.strptime(s, form)
        t = TimeUtils.pyTime(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo)
        return t
        
    @staticmethod
    def dayOfLastSunday(year, month):
        '''dow: Monday(0) - Sunday(6)'''
        dow = 6
        n = calendar.monthrange(year, month)[1]
        l = range(n - 6, n + 1)
        w = calendar.weekday(year, month, l[0])
        w_l = [i % 7 for i in range(w, w + 7)]
        return l[w_l.index(dow)]
    
    @staticmethod 
    def dayOfSunday(year, month, num):
        first = datetime(year, month, 1).weekday()
        day = 7 * num - first
        return day
    
    @staticmethod
    def utcTime(year, month, day, hour, minute, second):
        return TimeUtils.pyTime(year, month, day, hour, minute, second, pytz.timezone('UTC'))   
    
    #https://pytz.sourceforge.net/
    #Unfortunately using the tzinfo argument of the standard datetime constructors ‘’does not work’’ with pytz for many timezones.
    @staticmethod
    def pyTime(year, month, day, hour, minute, second, tzinfo):
        t = datetime(year, month, day, hour, minute, second)
        time = tzinfo.localize(t)
        return time
    
    @staticmethod
    def awarePytime2naive(time):
        naive = datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
        return naive

    @staticmethod
    def isSummerTime(date_time):
        day0 = TimeUtils.dayOfSunday(date_time.year, 3, 2)
        tsummer0 = TimeUtils.utcTime(date_time.year, 3, day0, 0, 0, 0)
        day1 = TimeUtils.dayOfSunday(date_time.year, 10, 2)
        tsummer1 = TimeUtils.utcTime(date_time.year, 10, day1, 0, 0, 0)
        if date_time > tsummer0 and date_time < tsummer1:
            return True
        else:
            return False
    
    @staticmethod
    def isSummerTime2(date_time):
        day0 = TimeUtils.dayOfLastSunday(date_time.year, 3)
        tsummer0 = TimeUtils.utcTime(date_time.year, 3, day0, 0, 0, 0)
        day1 = TimeUtils.dayOfLastSunday(date_time.year, 10)
        tsummer1 = TimeUtils.utcTime(date_time.year, 10, day1, 0, 0, 0)
        if date_time > tsummer0 and date_time < tsummer1:
            return True
        else:
            return False
        
    @staticmethod
    def timestamp2localtime(utc_server, tzinfo=None, adjust_summer_time=True):
        if tzinfo is None:
            t = datetime.fromtimestamp(utc_server)
        else:
            t = datetime.fromtimestamp(utc_server, tzinfo)
        if tzinfo is None or adjust_summer_time == False:
            return t
            
        if TimeUtils.isSummerTime(t):
            dt = 3
        else:
            dt = 2
        t -= timedelta(hours=dt)
        return t
    
    @staticmethod    
    def jst2timestamp(jst):
        timestamp = []
        for t in jst:
            timestamp.append(t.timestamp())
        return timestamp
    
    @staticmethod    
    def jst2utc(jst):
        utc = []
        for t in jst:
            utc.append(t.astimezone(timezone.utc))
        return utc
    
    @staticmethod        
    def numpyDateTime2pyDatetime(np_time):
        py_time = datetime.fromtimestamp(np_time.astype(datetime) * 1e-9)
        return py_time
    
    @staticmethod                
    def sliceTime(pytime_array: list, time_from, time_to):
        begin = None
        end = None
        for i in range(len(pytime_array)):
            t = pytime_array[i]
            if begin is None:
                if t >= time_from:
                    begin = i
            else:
                if t > time_to:
                    end = i
                    return (end - begin + 1, begin, end)
        if begin is not None:
            end = len(pytime_array) - 1
            return (end - begin + 1, begin, end)
        else:
            return (0, None, None)
    