from tester_trade_log.tester import Strategy

import datetime
import random


class ExampleStrategy(Strategy):
    def __init__(self, ticker: str, days=250):
        self.ticker = ticker
        self.days = days
        random.seed(1)

    def initialize(self, t):
        t.set_ticker(self.ticker)
        t.set_interval(datetime.timedelta(minutes=1))
        t.set_intervals_after_start(15)
        t.set_intervals_before_finish(15)
        t.set_trading_days(self.days)

    def tick(self, t):
        if random.random() < 0.05:
            t.open_position(duration=10)

    def on_start(self, t):
        pass

    def on_finish(self, t):
        pass
