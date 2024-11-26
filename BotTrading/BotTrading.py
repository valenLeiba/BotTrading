"""
Implementacion de la estrategia del bot de trading para la cursada de trading algoritmico 2024
"""
from __future__ import (absolute_import, division,print_function, unicode_literals)

import backtrader as bt 
import yfinance as yf
import pandas as pd
import matplotlib


class TestStrategy(bt.Strategy):
    params = (
        ('rapida_ma', 20),  # Período de la media móvil rápida
        ('lenta_ma', 50),  # Período de la media móvil lenta
        ('rsi_period', 20),  # Período del RSI
        ('boll_period', 20),  # Período de las bandas de Bollinger
    )

    def __init__(self):
        self.instruments = []
        for data in self.datas:
            # Indicadores
            sma_rapido = bt.indicators.SimpleMovingAverage(data, period=self.params.rapida_ma)
            sma_lento = bt.indicators.SimpleMovingAverage(data, period=self.params.lenta_ma)
            rsi = bt.indicators.RelativeStrengthIndex(data,period=self.params.rsi_period)
            boll = bt.indicators.BollingerBands(data, period=self.params.boll_period)

            self.instruments.append({
                'data': data,
                'sma_rapido': sma_rapido,
                'sma_lento': sma_lento,
                'rsi': rsi,
                'boll': boll,
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
        for instrument in self.instruments:
            if instrument['order'] == order:
                instrument['order'] = None

    def next(self):
        total_cash = self.broker.get_cash()
        
        for instrument in self.instruments:
            data = instrument['data']
            sma_rapido = instrument['sma_rapido']
            sma_lento = instrument['sma_lento']
            rsi = instrument['rsi']
            boll = instrument['boll']
            order = instrument['order']
            position = self.getposition(data)

            cash_por_instrumento = total_cash // len(self.datas)  # Divide el efectivo disponible entre los instrumentos
            size = int(cash_por_instrumento / data.close[0])  # Tamaño de la posición basado en el efectivo asignado

            # Condición de compra
            if not position and order is None:
                if sma_rapido[0] > sma_lento[0] or (rsi[0] < 40) or  (data.close[0] < boll.lines.bot[0]):  # Señal de tendencia alcista
                    self.log(f'BUY CREATE, {data.close[0]:.2f}')
                    instrument['order'] = self.buy(data=data, size=size)

            # Condición de venta
            elif position and order is None:
                if sma_rapido[0] < sma_lento[0] or rsi[0] > 65 or (data.close[0] > boll.lines.top[0] and self.position.size > 0):  # Señal de tendencia bajista
                    self.log(f'SELL CREATE, {data.close[0]:.2f}')
                    instrument['order'] = self.sell(data=data, size=position.size)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    # Lista de instrumentos (tickers)
    #instrumentos = ['XOM', 'CVX','BP']
    instrumentos = ['MSFT', 'GOOGL','AAPL']
    for instrumento in instrumentos:
        # Descargar datos con Yahoo Finance
        data = yf.download(instrumento, start='2020-01-01', end='2023-12-31')

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