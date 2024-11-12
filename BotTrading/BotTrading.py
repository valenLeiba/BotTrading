#pip intsal backtrader !!!!!!
from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
from datetime import datetime
import os.path
import sys
import yfinance as yf
import matplotlib as mp
import pandas as pd

# def simpleMovingAverage(dataSet): #Pasar como parametro el dataset
#     acumulado = 0
#     contador = 1
#     for i in dataSet:
#         acumulado += i[0]
#         contador +=1
#     return acumulado / contador # Algo asi...


class TestStrategy(bt.Strategy): #Estrategia solo de compra

    def __init__(self):
        self.dataclose = self.datas[0].close


    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' %(dt.isoformat(), txt))


    def next(self):
        #Estrategia de compra       /venta
        self.log('Close, %2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            if self.dataclose[-1] < self.dataclose[-2]:
                self.log('BUY CREATE, %2f'% self.dataclose[0])
                self.buy()




if __name__ == '__main__':

    # Se descargan los datos
    data = yf.download('ORCL', start='2019-1-1', end='2019-12-31')

    print(data.columns)

    # Se reacomoda el tipo de dato para que matchee con Pandas
    data = data.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume"
    })

    data.index = pd.to_datetime(data.index)
    
    #Create a Cerebro entity
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/ORCL-2019.txt') #Nombre del archivo
    
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath, 
    #     fromdate=datetime(2019, 1, 1), 
    #     todate=datetime(2019, 12, 31),
    #     reverse = False) 

    dataORCL = bt.feeds.PandasData(dataname=data)

    # data.to_csv("ORCL-2019.txt")
    cerebro.adddata(dataORCL)
    cerebro.broker.setcash(100000.0)

    print(cerebro.datas.index(1,0,20))

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    cerebro.plot()

    print('Final portfolio value: %.2f' % cerebro.broker.getvalue())

    # # Para utilizar yf(yfinance) en la consola -> 'pip install yfinance' o 'conda install yfinance'
    # df = yf.download("AAPL", start="2022-1-1", end="2022-12-31", interval="1d")
    
    # print(df.head(20))