from tester_trade_log.tester import Strategy, Tester
import datetime
import numpy as np
from collections import deque


class RSIStrategy(Strategy):
    def __init__(self, ticker, period, start_day_index, trading_days):
        self.ticker = ticker
        self.period = period
        self.start_day_index = start_day_index
        self.trading_days = trading_days
        self.changes_queue = deque()
        self.changes_sum = 0
        self.positive_changes_sum = 0
        self.last_price = 0
        self.first_tick = True
        self.rsi_history = []

    def initialize(self, t: "Tester"):
        t.set_ticker(self.ticker)
        t.set_interval(datetime.timedelta(minutes=1))
        t.set_start_day_index(self.start_day_index)
        t.set_trading_days(self.trading_days)
        t.set_intervals_after_start(self.period)
        t.set_intervals_before_finish(self.period)

    def tick(self, t: "Tester"):
        if not self.first_tick:
            new_change = t.get_price() - self.last_price
            self.last_price = t.get_price()
            old_change = self.changes_queue.popleft()
            self.changes_queue.append(new_change)
            self.changes_sum += abs(new_change) - abs(old_change)
            if old_change > 0:
                self.positive_changes_sum -= old_change
            if new_change > 0:
                self.positive_changes_sum += new_change
        self.first_tick = False
        rsi = self.rsi()
        # decision
        if rsi < 30:
            t.open_position(duration=self.period)
        self.rsi_history.append(rsi)

    def on_start(self, t: "Tester"):
        prices = np.array(t.get_prices())
        self.last_price = prices[-1]
        assert len(prices) == self.period
        changes = np.diff(prices)
        self.changes_queue = deque(changes)
        self.changes_sum = np.abs(changes).sum()
        self.positive_changes_sum = changes[changes > 0].sum()

    def on_finish(self, t: "Tester"):
        self.rsi_history.clear()
        self.changes_sum = 0
        self.positive_changes_sum = 0

    def rsi(self):
        if not self.changes_sum:
            return 50
        return self.positive_changes_sum / self.changes_sum * 100

    def _compute_rsi(self, prices):
        assert len(prices) >= self.period
