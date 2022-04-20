from tester_trade_log.tester import Strategy

import datetime
import random


class ExampleStrategy(Strategy):
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.cnt = 0
        self.dates = set()
        random.seed(1)

    def initialize(self, t):
        t.set_ticker(self.ticker)
        t.set_interval(datetime.timedelta(minutes=1))
        t.set_time_after_start(datetime.timedelta(minutes=15))
        t.set_time_before_finish(datetime.timedelta(minutes=15))
        t.set_trading_days(250)

    def tick(self, t):
        if random.random() < 0.05:
            t.open_position(duration=10)

    def on_start(self, t):
        pass

    def on_finish(self, t):
        pass
