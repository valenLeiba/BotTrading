from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
from datetime import datetime
import os.path
import sys
import yfinance as yf
import matplotlib as mp
import pandas as pd


class TestStrategy(bt.Strategy): #Estrategia solo de compra

    def __init__(self):
        self.instruments = []  # Lista para almacenar los indicadores SMA de cada instrumento
        for i, data in enumerate(self.datas):
            # Crear un SMA para cada instrumento y añadirlo a la lista
            rsi = bt.indicators.RelativeStrengthIndex()
            sma = bt.indicators.SimpleMovingAverage(data.close, period=14)
            order = None
            buyprice = None
            buycomm = None
            self.instruments.append({'data': data, 'sma': sma, 'diacompra': 0, 'rsi': rsi})

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' %(dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return #Orden de compra/venta enviada o aceptada.
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %(order.executed.price,order.executed.value,order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, %.2f, Cost: %.2f, Comm %.2f' %(order.executed.price,order.executed.value,order.executed.comm))
            self.bar_executed = len(self) #Guarda cuando la orden fue ejecutada

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, BRUTA %.2f, NETA %.2f' %(trade.pnl, trade.pnlcomm))

    def next(self):

        for instrument in self.instruments:
            data = instrument['data']
            sma = instrument['sma']
            diacompra = instrument['diacompra']
            rsi = instrument['rsi']
            # Imprimir el valor de cierre y SMA de cada instrumento
            self.log('%s Close: %.2f, SMA: %.2f, RSI: %.2f' %(data._name, data.close[0], sma[0], rsi[0]))

            # banda de bolinger > data close
            if (rsi[0] < 30 and rsi[-1] >=30) or (sma[0] > self.data.close[0]):
                self.log('BUY CREATE, %.2f' % data.close[0])
                self.order = self.buy(data=data)
                # Reiniciar contador después de una compra
                instrument['diacompra'] = 0

            elif self.getposition(data):
                instrument['diacompra'] += 1 #Parametro de salida
                #(rsi[0] > 70.0 and rsi[-1]<=70) or banda de bolinger < dataclose
                if (sma[0] < self.data.close[0]) or instrument['diacompra']==6:
                    self.log('SELL CREATE, %.2f' % data.close[0])
                    instrument['diacompra'] = 0
                    self.order = self.sell(data=data)
                



if __name__ == '__main__':

    #Create a Cerebro entity
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

   # Listado de instrumentos (tickers)
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    for ticker in tickers:
        data = yf.download(ticker, start='2019-1-1', end='2019-12-31')

        # Asegurarse de que los nombres de las columnas sean cadenas y no tuplas
        data.columns = [col[0] if isinstance(
            col, tuple) else col for col in data.columns]

        # Cambiar los nombres de las columnas a título (opcional)
        data.columns = [col.title() for col in data.columns]

        # Asegurarse de que el índice está en el formato de fecha y hora correcto
        data.index = pd.to_datetime(data.index)

        # Añadir cada conjunto de datos al cerebro, nombrándolos con el símbolo
        datafeed = bt.feeds.PandasData(dataname=data, name=ticker)
        cerebro.adddata(datafeed)

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final portfolio value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()