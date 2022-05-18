from tester_trade_log.tester import Strategy, Tester

from ta.momentum import RSIIndicator

import datetime
import pandas as pd


class RSIStrategy(Strategy):
    def __init__(self, length, duration, start_day_index, trading_days, check_crossing):
        self._length = length
        self._duration = duration
        self._start_day_index = start_day_index
        self._trading_days = trading_days
        self._check_crossing = check_crossing

        def rsi(**kwargs):
            return RSIIndicator(pd.Series(kwargs["close"])).rsi().values

        self._rsi = rsi

    def initialize(self, t: "Tester"):
        t.set_period(datetime.timedelta(minutes=1))
        t.set_start_day_index(self._start_day_index)
        t.set_trading_days(self._trading_days)
        t.set_periods_after_start(self._length - 1)
        t.set_periods_before_finish(self._duration)

        # rsi indicator
        t.add_indicator(self._rsi)

    def on_tick(self, t: "Tester"):
        # decision
        if self._check_crossing:
            rsi = t.get_today_indicator_history(0)
            if rsi[-1] > 30 >= rsi[-2]:
                t.buy(duration=self._duration)
            if rsi[-1] < 70 <= rsi[-2]:
                t.sell(duration=self._duration)
        else:
            rsi = t.get_current_indicator(0)
            if rsi < 30:
                t.buy(duration=self._duration)
            if rsi > 70:
                t.sell(duration=self._duration)

    def on_start(self, t: "Tester"):
        pass

    def on_finish(self, t: "Tester"):
        pass
