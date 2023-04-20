# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:21:36 2022

@author: IKU-Trader
"""

import pandas as pd
import MetaTrader5 as mt5
from mt5_const import mt5_const
from const import const
from time_utils import TimeUtils
from datetime import datetime

class Order:
    Kind = int 
    EntryBuy: Kind = 0
    EntrySell: Kind = 1
    CloseBuy: Kind = 2
    CloseSell: Kind = 3
    CancelOrder: Kind = 4
    
    How = int 
    MarketOrder: How = 0
    Limit: How = 1
    Stop: How = 2
    
    def __init__(self,  symbol: str,
                         lot: int, 
                         price: float, 
                         order_kind: Kind, 
                         order_how: How,
                         slippage: int,
                         stoploss: float,
                         takeprofit: float,
                         magic_number: int,
                         ticket: int):
        self.symbol = symbol
        if order_kind == Order.EntryBuy:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_BUY
            elif order_how == Order.Limit:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_BUY_LIMIT
            elif order_how == Order.Stop:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_BUY_STOP
        elif order_kind == Order.EntrySell:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_SELL
            elif order_how == Order.Limit:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_SELL_LIMIT
            elif order_how == Order.Stop:
                self.action = mt5.TRADE_ACTION_PENDING
                self.type = mt5.ORDER_TYPE_SELL_STOP
        elif order_kind == Order.CloseSell:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_SELL
        elif order_kind == Order.CloseBuy:
            if order_how == Order.MarketOrder:
                self.action = mt5.TRADE_ACTION_DEAL
                self.type = mt5.ORDER_TYPE_BUY            
        self.ticket = ticket
        self.lot = lot
        self.price = price
        self.magic_number = magic_number
        self.slippage = slippage
        self.stoploss = stoploss
        self.takeprofit = takeprofit

class BuyMarketOrder(Order):
    def __init__(self, symbol, lot, slippage, stoploss, takeprofit):
        price = mt5.symbol_info_tick(symbol).ask
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.MarketOrder,
                         slippage,
                         sl,
                         tp,
                         1000,
                         None)

class SellMarketOrder(Order):
    def __init__(self, symbol, lot, slippage, stoploss, takeprofit):
        price = mt5.symbol_info_tick(symbol).ask
        if stoploss is not None:
            sl = price + abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price - abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.MarketOrder,
                         slippage,
                         sl,
                         tp,
                         2001,
                         None)
        
class BuyLimitOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.Limit,
                         slippage,
                         sl,
                         tp,
                         1001,
                         None)
        
class SellLimitOrder(Order):
     def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
         if stoploss is not None:
             sl = price + abs(stoploss)
         else:
             sl = None
         if takeprofit is not None:
             tp = price - abs(takeprofit)
         else:
             tp = None
         super().__init__(symbol,
                          lot,
                          price,
                          Order.EntrySell,
                          Order.Limit,
                          slippage,
                          sl,
                          tp,
                          2002,
                          None) 
         
class BuyStopOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.Stop,
                         slippage,
                         sl,
                         tp,
                         1002,
                         None)

class SellStopOrder(Order):
    def __init__(self, symbol, lot, price, slippage, stoploss, takeprofit):
        if stoploss is not None:
            sl = price - abs(stoploss)
        else:
            sl = None
        if takeprofit is not None:
            tp = price + abs(takeprofit)
        else:
            tp = None
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.Stop,
                         slippage,
                         sl,
                         tp,
                         2003,
                         None)        
        
class CloseBuyPostionMarketOrder(Order):
    def __init__(self, symbol, lot, ticket):
        price = mt5.symbol_info_tick(symbol).bid
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntrySell,
                         Order.MarketOrder,
                         None,
                         None,
                         None,
                         3001,
                         ticket)    
    
class CloseSellPostionMarketOrder(Order):
    def __init__(self, symbol, lot, ticket):
        price = mt5.symbol_info_tick(symbol).bid
        super().__init__(symbol,
                         lot,
                         price,
                         Order.EntryBuy,
                         Order.MarketOrder,
                         None,
                         None,
                         None,
                         3002,
                         ticket)        
        
class PyMT5(object):
    def __init__(self, timezone):
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        print('MetaTrader5 connected, API Ver: ', mt5.version())
        self.tzinfo = timezone
    
    def close(self):
        mt5.shutdown()
    
    def convert(self, data: list):
        if data is None:
            return ([], {})
        localtime = []
        arrays = []
        for i in range(5):
            arrays.append([])
        for d in data:
            values = list(d)
            time = TimeUtils.timestamp2localtime(values[0], tzinfo=self.tzinfo)
            localtime.append(time)
            for i in range(5):
                if i == 4:
                    j = 7
                else:
                    j = i + 1
                arrays[i].append(values[j])
        dic = {}
        dic[const.TIME] = localtime
        dic[const.OPEN] = arrays[0]
        dic[const.HIGH] = arrays[1]
        dic[const.LOW] = arrays[2]
        dic[const.CLOSE] = arrays[3]
        dic[const.VOLUME] = arrays[4]
        return dic
     
    def download(self, symbol: str, timeframe: str, size: int=99999):
        d = mt5.copy_rates_from_pos(symbol, mt5_const.TIMEFRAME[timeframe][0] , 0, size) 
        return self.convert(d)

    def downloadRange(self, symbol: str, timeframe: str, begin_jst: datetime, end_jst: datetime):
        utc_from = TimeUtils.jst2serverTime(begin_jst)
        utc_to = TimeUtils.jst2serverTime(end_jst)
        d = mt5.copy_rates_range(symbol, mt5_const.TIMEFRAME[timeframe][0] , utc_from, utc_to) 
        return self.convert(d)
    
    def downloadTicks(self, symbol: str, timeframe: str, from_jst: datetime, size: int=100000):
        utc_from = TimeUtils.jst2serverTime(from_jst)
        d = mt5.copy_ticks_from(symbol, mt5_const.TIMEFRAME[timeframe][0] , utc_from, size, mt5.COPY_TICKS_ALL) 
        return self.convert(d)
    
    def accountInfo(self):
        info = mt5.account_info()
        if info is None:
            print("Retreiving account information failed")
            return None
        
        data = [info.balance, info.credit, info.profit, info.equity, info.margin, info.margin_free, info.margin_level, info.margin_so_call, info.currency]
        columns = ['balance', 'credit', 'profit', 'equity', 'margin', 'margin_free', 'margin_level', 'margin_so_call', 'currency']         
        return pd.DataFrame(data=[data], columns=columns)

    def checkSymbol(self, symbol: str):
        info = mt5.symbol_info(symbol)
        if info is None:
            return False
        else:
            return True

    def positions(self, symbol: str):
        if symbol is None:
            pos = mt5.positions_get()
        else:
            if symbol.strip() == '':
                pos = mt5.positions_get()
            else:
                pos = mt5.positions_get(group='*'+symbol+'*')
        buy_positions = []
        sell_positions = []
        for p in pos:
            dic = p._asdict()
            order_type = dic['type']
            if order_type == 0:
                typ = 'buy'
            else:
                typ = 'sell'
            time = dic['time']
            t = TimeUtils.timestamp2localtime(time, tzinfo=TimeUtils.TIMEZONE_TOKYO)
            values = [typ, t, dic['symbol'], dic['volume'], dic['ticket'], dic['profit'], dic['sl'], dic['tp']]
            if order_type == 0: # buy position
                buy_positions.append(values)
            elif order_type == 1: # sellポジションの場合
                sell_positions.append(values)
                
        columns = ['type', 'time', 'symbol', 'volume', 'ticket', 'profit', 'stoploss', 'takeprofit']    
        df_buy = pd.DataFrame(data=buy_positions, columns=columns)
        df_sell = pd.DataFrame(data=sell_positions, columns=columns)
        return (df_buy, df_sell)
    
    def position(self, ticket):
        dic = {}
        pos = mt5.positions_get(ticket=ticket)
        if len(pos) == 0:
            return None
        p = pos[0]
        dic = p._asdict()
        return dic

    def buyMarketOrder(self, symbol: str, lot:int, slippage=None, stoploss=None, takeprofit=None):
        order = BuyMarketOrder(symbol, lot, slippage, stoploss, takeprofit)
        return self.sendOrder(order)
        
    def sellMarketOrder(self, symbol: str, lot:int, slippage=None, stoploss=None, takeprofit=None):
        order = SellMarketOrder(symbol, lot, slippage, stoploss, takeprofit)
        return self.sendOrder(order)
            
    def sendOrder(self, order: Order):
        request = {
                    'action': order.action,
                    'symbol': order.symbol,                
                    'type': order.type,
                    'volume': order.lot,
                    'price': order.price,
                    'comment': 'By python API',
                    'magic': order.magic_number,
                    'type_time': mt5.ORDER_TIME_GTC,
                    'type_filling': mt5.ORDER_FILLING_IOC,
                    }
        if order.ticket is not None:
            request['position'] = order.ticket
        if order.slippage is not None:
            request['deviation'] = order.slippage
        if order.stoploss is not None:
            request['sl'] = order.stoploss
        if order.takeprofit is not None:
            request['tp'] = order.takeprofit       
            
        result = mt5.order_send(request)
        dic = {}
        dic['retcode'] = result.retcode
        dic['ticket'] = result.order
        dic['volume'] = result.volume
        dic['price'] = result.price

        return ((result.retcode == 10009), dic) 

    def closeBuyPositionMarketOrder(self, symbol: str, lot: int, ticket: int):    
        order = CloseBuyPostionMarketOrder(symbol, lot, ticket)
        return self.sendOrder(order)
    
    def closeSellPositionMarketOrder(self, symbol: str, lot: int, ticket: int):    
        order = CloseSellPostionMarketOrder(symbol, lot, ticket)
        return self.sendOrder(order)

    def closeAll(self, symbol: str):
        (df_buy, df_sell) = self.positions(symbol) 
        for i in range(len(df_buy)):
            d = df_buy.iloc[i, :]
            self.closeBuyPositionMarketOrder(d['symbol'], float(d['volume']), int(d['ticket']))
        for i in range(len(df_sell)):
            d = df_sell.iloc[i, :]
            self.closeSellPositionMarketOrder(d['symbol'], float(d['volume']), int(d['ticket']))    

def test():
    server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
    dic = server.download('DOWUSD', 'M1', 5)
    info = server.accountInfo()
    print(info)
    
    dic = server.position(1230514)
    (df_buy, df_sell) = server.positions('')
    print(df_buy)
    print(df_sell)
    server.closeAll('')
    
if __name__ == '__main__':
    test()