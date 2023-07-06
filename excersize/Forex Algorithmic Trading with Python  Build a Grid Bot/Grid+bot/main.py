import MetaTrader5 as mt5
import pandas as pd
from classes import Bot
from threading import Thread




mt5.initialize(login = 51061338,server = "ICMarketsSC-Demo",password ="kycpV2QK")

bot1 = Bot(10,"EURUSD",0.01,2,1)
bot2 = Bot(10,"GBPUSD",0.01,2,1)
bot3 = Bot(10,"USDCHF",0.01,2,1)

def b1():
    bot1.run()
def b2():
    bot2.run()
def b3():
    bot3.run()

thread1 = Thread(target=b1)
thread2 = Thread(target=b2)
thread3 = Thread(target=b3)

thread1.start()
thread2.start()
thread3.start()




