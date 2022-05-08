from tester_trade_log.tester import Tester, Strategy, DIRECTION

import datetime
import random


class ExampleStrategy(Strategy):
    def __init__(self, ticker: str, days=250):
        self.ticker = ticker
        self.days = days
        random.seed(1)

    def initialize(self, t: "Tester"):
        t.set_ticker(self.ticker)
        t.set_period(datetime.timedelta(minutes=1))
        t.set_periods_after_start(15)
        t.set_periods_before_finish(15)
        t.set_start_day_index(0)
        t.set_trading_days(self.days)

    def on_tick(self, t: "Tester"):
        # positions
        if t.is_open_position():
            # position is open
            pass
        if random.random() < 0.05:
            t.open_position(DIRECTION.LONG, duration=10)
            # t.buy(duration=10) # the same
        elif random.random() < 0.05:
            t.sell(duration=10)
        elif random.random() < 0.05:
            t.close_position()
        # current values
        current_price = t.get_current_price()
        current_volume = t.get_current_volume()
        current_time = t.get_current_time()

        # today history values
        today_price_history = t.get_today_price_history()
        today_volume_history = t.get_today_volume_history()

        # general information
        close_price_history_by_day = t.get_day_close_price_history()
        days = t.get_days_history()
        trades = t.get_trades_history()
        ticker = t.get_ticker()

    def on_start(self, t: "Tester"):
        # today start
        pass

    def on_finish(self, t: "Tester"):
        # today finish
        pass
