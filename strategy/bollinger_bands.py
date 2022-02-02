import datetime
import math
import numpy as np

from strategy.base import BaseStrategy


class BollingerBands(BaseStrategy):
    def __init__(self, equity: str, cash: float, date=datetime.date.today(), n=10):
        self.equity: str = equity
        self.cash: float = cash
        self.date = date
        self.n = n

    def initialize(self, t):
        t.add_equity(self.equity)
        t.set_cash(self.cash)
        t.set_start(self.date)
        t.set_end(self.date + datetime.timedelta(days=1))
        t.set_interval("1m")

    def make_tick(self, t):
        price = t.get_price(self.equity)
        prices = t.get_equity_price_history(self.equity)[-self.n :]
        if len(prices) < self.n:
            return

        avg = np.mean(prices)
        std = np.std(prices)
        number = round(math.floor(self.cash / price / 10))
        if price > avg + std:
            t.create_order(-number, self.equity, duration=10)
        elif price < avg - std:
            t.create_order(number, self.equity, duration=10)
