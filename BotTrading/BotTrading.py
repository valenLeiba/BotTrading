"""
Implementacion de la estrategia del bot de trading para la cursada de trading algoritmico 2024
"""
from __future__ import (absolute_import, division,print_function, unicode_literals)

import backtrader as bt
import yfinance as yf
import pandas as pd



class TestStrategy(bt.Strategy):
    def __init__(self):
        self.indicadores = []
        for data in self.datas:
            # Indicadores
            rsi = bt.indicators.RelativeStrengthIndex(data, period=14)
            boll = bt.indicators.BollingerBands(data, period=20)
            macd = bt.indicators.MACD(data, period_me1 = 12, period_me2 = 26, period_signal = 9)
            # macd = bt.indicators.MACD(data, fast=12, slow=26, signal=9)

            self.indicadores.append({
                'data': data,
                'rsi': rsi,
                'boll': boll,
                'macd': macd,
                'order': None
            })

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Limpiar referencia a la orden
        for indicador in self.indicadores:
            if indicador['order'] == order:
                indicador['order'] = None

    def next(self):
        for indicador in self.indicadores:
            data = indicador['data']
            rsi = indicador['rsi']
            boll = indicador['boll']
            macd = indicador['macd']
            order = indicador['order']

            # Cálculo del histograma del MACD
            macd_hist = macd.macd[0] - macd.signal[0]

            # Condición de compra
            if not self.getposition(data) and order is None:
                if (rsi[0] < 30 and rsi[-1] >= 30) or \
                   (data.close[0] < boll.lines.bot[0]) or \
                   (macd_hist > 0 and macd.macd[-1] - macd.signal[-1] <= 0):
                    self.log(f'BUY CREATE, {data.close[0]:.2f}')
                    indicador['order'] = self.buy(data=data)

            # Condición de venta
            elif self.getposition(data) and order is None:
                if (rsi[0] > 70 and rsi[-1] <= 70) or \
                   (data.close[0] > boll.lines.top[0]) or \
                   (macd_hist < 0 and macd.macd[-1] - macd.signal[-1] >= 0):
                    self.log(f'SELL CREATE, {data.close[0]:.2f}')
                    indicador['order'] = self.sell(data=data)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    # Lista de instrumentos (tickers)
    # instrumentos = ['BBAR', 'TSLA', 'KO']
    instrumentos = ['AAPL', 'MSFT', 'GOOGL']
    for instrumento in instrumentos:
        # Descargar datos con Yahoo Finance
        data = yf.download(instrumento, start='2023-01-01', end='2023-12-31')

        # Ajustar los datos
        data.columns = [col[0] if isinstance(
            col, tuple) else col for col in data.columns]
        data.index = pd.to_datetime(data.index)
        datafeed = bt.feeds.PandasData(dataname=data, name=instrumento)
        cerebro.adddata(datafeed)

    # Configurar el broker
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    start_portfolio = cerebro.broker.getvalue()
    cerebro.run()
    print('Starting Portfolio Value: %.2f' % start_portfolio)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot()
