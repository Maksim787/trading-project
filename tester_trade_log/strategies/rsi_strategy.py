from tester_trade_log.tester import Strategy, Tester
from tester_trade_log.indicators.rsi import RSI
import datetime


class RSIStrategy(Strategy):
    def __init__(self, length, start_day_index, trading_days):
        self._length = length
        self._start_day_index = start_day_index
        self._trading_days = trading_days
        self._rsi = RSI(length)

    def initialize(self, t: "Tester"):
        t.set_period(datetime.timedelta(minutes=1))
        t.set_start_day_index(self._start_day_index)
        t.set_trading_days(self._trading_days)
        t.set_periods_after_start(self._length)
        t.set_periods_before_finish(self._length)

        # rsi indicator
        t.add_indicator(self._rsi)

    def on_tick(self, t: "Tester"):
        rsi = self._rsi.get_current_value()
        # decision
        if rsi < 30:
            t.buy(duration=self._length)
        if rsi > 70:
            t.sell(duration=self._length)

    def on_start(self, t: "Tester"):
        pass

    def on_finish(self, t: "Tester"):
        pass
