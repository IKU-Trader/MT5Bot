
import MetaTrader5 as mt5
import pandas as pd


class Bot:
    def __init__(self,n,symbol,volume,profit_target,proportion):
        self.n = n
        self.symbol = symbol
        self.volume = volume
        self.profit_target = profit_target
        self.proportion = proportion

    def buy_limit(self,symbol, volume, price):
        request = mt5.order_send({
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": price,
            "deviation": 20,
            "magic": 100,
            "comment": "python market order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        })

        print(request)

    def sell_limit(self,symbol, volume, price):
        request = mt5.order_send({
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": price,
            "deviation": 20,
            "magic": 100,
            "comment": "python market order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        })

        print(request)

    def cal_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        profit = float(df["profit"].sum())
        return profit

    def cal_volume(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        profit = float(df["volume"].sum())
        return profit

    def cal_buy_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 0]
        profit = float(df["profit"].sum())
        return profit

    def cal_sell_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 1]
        profit = float(df["profit"].sum())
        return profit

    def cal_buy_margin(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 0]

        sum = 0
        for i in df.index:
            volume = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, volume, open_price)
            sum += margin
        return sum

    def cal_sell_margin(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 1]

        sum = 0
        for i in df.index:
            volume = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_SELL, symbol, volume, open_price)
            sum += margin
        return sum

    def cal_pct_buy_profit(self,symbol):
        profit = self.cal_buy_profit(symbol)
        margin = self.cal_buy_margin(symbol)
        pct = (profit / margin) * 100
        return pct

    def cal_pct_sell_profit(self,symbol):
        profit = self.cal_sell_profit(symbol)
        margin = self.cal_sell_margin(symbol)
        pct = (profit / margin) * 100
        return pct

    def close_position(self,position):
        tick = mt5.symbol_info_tick(position.symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": 20,
            "magic": 100,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result

    def close_all(self,symbol):
        position = mt5.positions_get(symbol=symbol)
        for position in position:
            self.close_position(position)

    def delete_pending(self,ticket):
        close_request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": ticket,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            result_dict = result._asdict()
            print(result_dict)
        else:
            print('Delete complete...')

    def close_limit(self,symbol):
        orders = mt5.orders_get(symbol=symbol)
        df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
        df.drop(['time_done', 'time_done_msc', 'position_id', 'position_by_id', 'reason', 'volume_initial',
                 'price_stoplimit'], axis=1, inplace=True)
        df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
        for ticket in df.ticket:
            self.delete_pending(ticket)

    def run(self):
        while True:
            pct_change = 1
            tick = mt5.symbol_info_tick(self.symbol)
            current_price_sell = tick.bid
            adj_sell = 1.2

            for i in range(self.n):
                price = ((pct_change / (100 * 100)) * current_price_sell) * adj_sell * self.proportion + current_price_sell
                self.sell_limit(self.symbol, self.volume, price)
                pct_change += 1
                adj_sell += 0.2

            pct_change_2 = -1
            tick = mt5.symbol_info_tick(self.symbol)
            current_price_buy = tick.ask
            adj_buy = 1.2

            for i in range(self.n):
                price = ((pct_change_2 / (100 * 100)) * current_price_buy) * adj_buy * self.proportion + current_price_buy
                self.buy_limit(self.symbol, self.volume, price)
                pct_change_2 -= 1
                adj_buy += 0.2

            while True:
                position = mt5.positions_get(symbol=self.symbol)
                if len(position) > 0:
                    margin_s = self.cal_sell_margin(self.symbol)
                    margin_b = self.cal_buy_margin(self.symbol)

                    if margin_s > 0:
                        try:
                            pct_sell_profit = self.cal_pct_sell_profit(self.symbol)
                            if pct_sell_profit >= self.profit_target:
                                self.close_all(self.symbol)
                        except:
                            pass

                    if margin_b > 0:
                        try:
                            pct_buy_profit = self.cal_pct_buy_profit(self.symbol)
                            if pct_buy_profit >= self.profit_target:
                                self.close_all(self.symbol)
                        except:
                            pass

                    position = mt5.positions_get(symbol=self.symbol)
                    if len(position) == 0:
                        self.close_limit(self.symbol)
                        break

