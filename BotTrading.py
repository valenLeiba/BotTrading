#from __future__ import (absolute_import, diviison, print_function, unicode_literals)
#pip intsal backtrader !!!!!!
import backtrader as bt
import datetime

class testStrategy(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0].close
    

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)

    def next():
        #Estrategia de compra/venta
        return 0


if __name__ == '__main__':

    #Create a Cerebro entity
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100.0)

    #Faltaria descargar los data feeds y agregar lo de la filmina 63 y 64


    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    
    print('Final portfolio value: %.2f' % cerebro.broker.getvalue())
