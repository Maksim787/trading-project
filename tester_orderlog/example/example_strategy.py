from tester_orderlog.tester import Strategy, Direction

import random
import datetime


class ExampleStrategy(Strategy):
    def __init__(self, ticker: str):
        self.ticker = ticker

    def initialize(self, t):
        t.set_ticker(self.ticker)
        t.set_start_period(datetime.timedelta(minutes=15))
        t.set_finish_period(datetime.timedelta(minutes=15))
        t.set_trading_days(10)

    def tick(self, t):
        if random.random() > 0.5:
            t.place_limit_order(Direction.Buy, 0, 2500)
        else:
            t.place_limit_order(Direction.Sell, float("+inf"), 2500)
        close_price = t.get_close()
        if random.random() > 0.5:
            t.place_limit_order(Direction.Buy, close_price * 0.99, 2500)
        else:
            t.place_limit_order(Direction.Sell, close_price * 1.01, 2500)
