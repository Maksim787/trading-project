from tester_trade_log.tester import Indicator, Tester
from collections import deque
import numpy as np


class RSI(Indicator):
    def __init__(self, length):
        self._length = length
        self._changes_queue = deque()
        self._total_sum = 0
        self._positive_sum = 0
        self._last_price = None
        self._rsi_history = []

    def get_init_periods(self) -> int:
        return self._length

    def initialize(self, t: "Tester"):
        prices = t.get_today_price_history()
        assert len(prices) == self._length
        self._last_price = prices[-1]
        changes = np.diff(prices)
        self._changes_queue = deque(map(float, changes))
        self._total_sum = float(np.abs(changes).sum())
        self._positive_sum = float(changes[changes > 0].sum())
        self._rsi_history.append(self.get_current_value())

    def on_tick(self, t: "Tester"):
        new_price = t.get_current_price()
        new_change = new_price - self._last_price
        self._last_price = new_price
        old_change = self._changes_queue.popleft()
        self._changes_queue.append(new_change)
        self._total_sum += abs(new_change) - abs(old_change)
        if new_change > 0:
            self._positive_sum += new_change
        if old_change > 0:
            self._positive_sum -= old_change
        self._rsi_history.append(self.get_current_value())

    def get_current_value(self):
        return self._positive_sum / self._total_sum * 100 if self._total_sum else 50

    def get_values_history(self):
        return self._rsi_history

    def clear(self, t: "Tester"):
        self._rsi_history.clear()
        self._last_price = None
