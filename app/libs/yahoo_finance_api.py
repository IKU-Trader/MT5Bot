# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 14:03:14 2023

@author: IKU-Trader
"""

import polars as pl
from .time_utils import TimeUtils
from yahoo_finance_api2 import share as api
from yahoo_finance_api2.exceptions import YahooFinanceError
import pytz


TIMEZONE_TOKYO = pytz.timezone('Asia/Tokyo')
TIMEZONE_NY = pytz.timezone('America/New_York')


class YahooFinanceApi:
    TIMEFRAMES = {'M1': [api.PERIOD_TYPE_DAY, 3,  api.FREQUENCY_TYPE_MINUTE, 1],
                  'M5': [api.PERIOD_TYPE_DAY, 10,  api.FREQUENCY_TYPE_MINUTE, 5],
                  'M15':[api.PERIOD_TYPE_DAY, 20,  api.FREQUENCY_TYPE_MINUTE, 15],
                  'M30':[api.PERIOD_TYPE_DAY, 30,  api.FREQUENCY_TYPE_MINUTE, 30],
                  'H1': [api.PERIOD_TYPE_DAY, 50,  api.FREQUENCY_TYPE_HOUR, 1],
                  'D1': [api.PERIOD_TYPE_WEEK, 100, api.FREQUENCY_TYPE_DAY, 1] }

    @staticmethod
    def download(symbol, param, tzinfo):
        yahoo_finance = api.Share(symbol)
        try:
            data = yahoo_finance.get_historical(param[0], param[1], param[2], param[3])
            timestamps = data['timestamp']
            times = [TimeUtils.timestamp2localtime(int(t/1000), tzinfo=tzinfo) for t in timestamps]
            d = {'time': times, 'open': data['open'], 'high': data['high'], 'low': data['low'], 'close': data['close']}
            df = pl.DataFrame(d)
            return df
        except YahooFinanceError as e:
            print(e.message)
            return None

if __name__ == "__main__":
    data = YahooFinanceApi.download('MSFT', 'D1', TIMEZONE_NY)
    print(data)