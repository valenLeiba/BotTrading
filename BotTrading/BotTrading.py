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
        self.diacompra = 0
        # self.isBuy = False
        

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' %(dt.isoformat(), txt))


    def next(self):

        self.log('Close, %2f' % self.dataclose[0])

        # Corregir porque compra el 3/1 porque toma el cierre del -1 que seria el 30/12/19!!!!!
        if not self.position:
            # Estrategia de compra luego de 2 dias de bajas
            if self.dataclose[0] < self.dataclose[-1]:
                if (self.dataclose[-1] < self.dataclose[-2]): # and not self.isBuy):
                    self.log('BUY CREATE, %2f' % self.dataclose[0])
                    # self.isBuy = True
                    self.buy()

        elif self.position:
            self.diacompra += 1

            # # Estrategia de venta luego de 6 dias
            if self.diacompra == 7:
                self.log('SELL CREATE, %2f' % self.dataclose[0])
                self.diacompra = 0
                # self.isBuy = False
                self.sell()



if __name__ == '__main__':

    #Create a Cerebro entity
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    # Se descargan los datos
    dataORCL = pd.DataFrame()
    data = yf.download('ORCL', start='2019-1-1', end='2019-12-31')

    # Se acomodan los nombres de las columnas al formato deseado, de tuplas pasan a ser columnas de un solo valor.
    data.columns = [' '.join(col).strip() for col in data.columns.values]
    data.columns = [col.replace(' ORCL', '') for col in data.columns]
    data.columns = [col.title() for col in data.columns] # Renombre las columas con mayusculas
    print(type(data.columns))
    print(data.columns)

    # Se transforman los datos a tipo Pandas.DataFrame, que es lo que recibe el metodo run()
    data.index = pd.to_datetime(data.index)
    dataORCL = bt.feeds.PandasData(dataname=data)

    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, '../../datas/ORCL-2019.txt') #Nombre del archivo 

    # data.to_csv("ORCL-2019.txt")
    cerebro.adddata(dataORCL)
    cerebro.broker.setcash(100000.0)

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final portfolio value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()