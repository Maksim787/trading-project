from tester_trade_log.tester import Strategy, Tester
import datetime
import unittest
import random


class TestStrategy(Strategy):
    def __init__(self, ticker):
        self.ticker = ticker
        self.dates = []
        self.prices = []
        self.volumes = []
        self.start_dates = []
        self.finish_dates = []

    def initialize(self, t):
        t.set_ticker(self.ticker)
        t.set_period(datetime.timedelta(minutes=30))
        t.set_trading_days(5)

    def on_tick(self, t):
        self.dates.append(t.get_current_time().strftime("%Y/%m/%d %H:%M:%S"))
        self.prices.append(t.get_current_price())
        self.volumes.append(t.get_current_volume())

    def on_start(self, t):
        self.start_dates.append(t.get_current_time().strftime("%Y/%m/%d %H:%M:%S"))

    def on_finish(self, t):
        self.finish_dates.append(t.get_current_time().strftime("%Y/%m/%d %H:%M:%S"))


class TestTradeStrategy(Strategy):
    def __init__(self, ticker):
        self.ticker = ticker
        self.durations = []

    def initialize(self, t):
        random.seed(1)
        t.set_ticker(self.ticker)
        t.set_period(datetime.timedelta(minutes=30))
        t.set_trading_days(5)

    def on_tick(self, t):
        if t.is_open_position():
            return
        if random.random() >= 0.5:
            duration = random.randint(1, 10)
            self.durations.append(duration)
            t.buy(duration=duration)

    def on_start(self, t):
        pass

    def on_finish(self, t):
        pass


class TestTradeLog(unittest.TestCase):
    def test_trade_log_ticks(self):
        strategy = TestStrategy("TEST_TICKER")
        tester = Tester("tester_trade_log/tests", strategy)
        tester.test()
        ticks = [" ".join([str(date), str(price), str(volume)]) for date, price, volume in zip(strategy.dates, strategy.prices, strategy.volumes)]
        self.assertEqual(
            strategy.start_dates, ["2015/03/02 10:30:00", "2015/03/03 10:30:00", "2015/03/04 10:30:00", "2015/03/05 10:30:00", "2015/03/06 10:30:00"]
        )
        self.assertEqual(
            strategy.finish_dates, ["2015/03/02 18:30:00", "2015/03/03 18:30:00", "2015/03/04 18:30:00", "2015/03/05 18:30:00", "2015/03/06 18:30:00"]
        )
        self.assertEqual(
            ticks,
            [
                "2015/03/02 10:30:00 174.9 120",
                "2015/03/02 11:00:00 175.5 770",
                "2015/03/02 11:30:00 179.1 270",
                "2015/03/02 12:00:00 178.6 50",
                "2015/03/02 12:30:00 175.8 380",
                "2015/03/02 13:00:00 175.8 0",
                "2015/03/02 13:30:00 176.0 80",
                "2015/03/02 14:00:00 176.0 0",
                "2015/03/02 14:30:00 175.9 90",
                "2015/03/02 15:00:00 173.8 100",
                "2015/03/02 15:30:00 174.8 330",
                "2015/03/02 16:00:00 174.0 5000",
                "2015/03/02 16:30:00 174.0 0",
                "2015/03/02 17:00:00 173.9 390",
                "2015/03/02 17:30:00 173.0 110",
                "2015/03/02 18:00:00 171.8 10",
                "2015/03/02 18:30:00 172.7 90",
                "2015/03/03 10:30:00 171.5 110",
                "2015/03/03 11:00:00 170.9 40",
                "2015/03/03 11:30:00 170.9 0",
                "2015/03/03 12:00:00 172.4 20",
                "2015/03/03 12:30:00 173.9 70",
                "2015/03/03 13:00:00 174.7 50",
                "2015/03/03 13:30:00 175.0 120",
                "2015/03/03 14:00:00 174.7 10",
                "2015/03/03 14:30:00 174.7 0",
                "2015/03/03 15:00:00 174.7 0",
                "2015/03/03 15:30:00 174.7 0",
                "2015/03/03 16:00:00 175.0 60",
                "2015/03/03 16:30:00 175.0 0",
                "2015/03/03 17:00:00 175.0 0",
                "2015/03/03 17:30:00 173.5 40",
                "2015/03/03 18:00:00 173.5 0",
                "2015/03/03 18:30:00 174.6 760",
                "2015/03/04 10:30:00 177.0 170",
                "2015/03/04 11:00:00 177.5 500",
                "2015/03/04 11:30:00 177.8 50",
                "2015/03/04 12:00:00 174.9 270",
                "2015/03/04 12:30:00 174.9 0",
                "2015/03/04 13:00:00 174.9 0",
                "2015/03/04 13:30:00 175.4 30",
                "2015/03/04 14:00:00 175.4 0",
                "2015/03/04 14:30:00 174.0 3000",
                "2015/03/04 15:00:00 174.0 0",
                "2015/03/04 15:30:00 174.0 0",
                "2015/03/04 16:00:00 174.0 0",
                "2015/03/04 16:30:00 175.6 10",
                "2015/03/04 17:00:00 175.6 0",
                "2015/03/04 17:30:00 175.6 0",
                "2015/03/04 18:00:00 175.6 0",
                "2015/03/04 18:30:00 173.0 30",
                "2015/03/05 10:30:00 173.7 100",
                "2015/03/05 11:00:00 173.7 0",
                "2015/03/05 11:30:00 173.7 0",
                "2015/03/05 12:00:00 173.1 40",
                "2015/03/05 12:30:00 173.1 0",
                "2015/03/05 13:00:00 172.5 10",
                "2015/03/05 13:30:00 172.5 0",
                "2015/03/05 14:00:00 172.5 0",
                "2015/03/05 14:30:00 172.5 0",
                "2015/03/05 15:00:00 172.2 400",
                "2015/03/05 15:30:00 172.2 0",
                "2015/03/05 16:00:00 174.5 80",
                "2015/03/05 16:30:00 174.5 0",
                "2015/03/05 17:00:00 173.5 50",
                "2015/03/05 17:30:00 173.4 100",
                "2015/03/05 18:00:00 173.4 0",
                "2015/03/05 18:30:00 172.3 10",
                "2015/03/06 10:30:00 173.1 10",
                "2015/03/06 11:00:00 174.0 330",
                "2015/03/06 11:30:00 172.2 10",
                "2015/03/06 12:00:00 171.1 10",
                "2015/03/06 12:30:00 172.5 670",
                "2015/03/06 13:00:00 172.5 0",
                "2015/03/06 13:30:00 171.9 100",
                "2015/03/06 14:00:00 171.9 50",
                "2015/03/06 14:30:00 171.9 0",
                "2015/03/06 15:00:00 171.9 0",
                "2015/03/06 15:30:00 171.9 0",
                "2015/03/06 16:00:00 171.5 50",
                "2015/03/06 16:30:00 171.5 0",
                "2015/03/06 17:00:00 171.0 360",
                "2015/03/06 17:30:00 171.0 0",
                "2015/03/06 18:00:00 170.5 100",
                "2015/03/06 18:30:00 170.5 0",
            ],
        )

    def test_trade_log_trades(self):
        strategy = TestTradeStrategy("TEST_TICKER")
        tester = Tester("tester_trade_log/tests", strategy)
        tester.test()
        trades = tester.get_trades_history()
        for day_trades in trades:
            for i, trade in enumerate(day_trades):
                day_trades[i] = str(trade)
        self.assertEqual(strategy.durations, [2, 4, 7, 1, 5, 4, 2, 1, 1, 7, 7, 9, 9, 2, 5, 9])
        self.assertEqual(
            trades,
            [
                [
                    "Trade(open_time=2015-03-02 11:00:00, close_time=2015-03-02 12:00:00, open_price=175.5, close_price=178.6)",
                    "Trade(open_time=2015-03-02 13:30:00, close_time=2015-03-02 15:30:00, open_price=176.0, close_price=174.8)",
                    "Trade(open_time=2015-03-02 16:30:00, close_time=2015-03-02 18:30:00, open_price=174.0, close_price=172.7)",
                ],
                [
                    "Trade(open_time=2015-03-03 10:30:00, close_time=2015-03-03 11:00:00, open_price=171.5, close_price=170.9)",
                    "Trade(open_time=2015-03-03 11:00:00, close_time=2015-03-03 13:30:00, open_price=170.9, close_price=175.0)",
                    "Trade(open_time=2015-03-03 13:30:00, close_time=2015-03-03 15:30:00, open_price=175.0, close_price=174.7)",
                    "Trade(open_time=2015-03-03 15:30:00, close_time=2015-03-03 16:30:00, open_price=174.7, close_price=175.0)",
                    "Trade(open_time=2015-03-03 16:30:00, close_time=2015-03-03 17:00:00, open_price=175.0, close_price=175.0)",
                    "Trade(open_time=2015-03-03 17:30:00, close_time=2015-03-03 18:00:00, open_price=173.5, close_price=173.5)",
                    "Trade(open_time=2015-03-03 18:00:00, close_time=2015-03-03 18:30:00, open_price=173.5, close_price=174.6)",
                ],
                [
                    "Trade(open_time=2015-03-04 10:30:00, close_time=2015-03-04 14:00:00, open_price=177.0, close_price=175.4)",
                    "Trade(open_time=2015-03-04 14:00:00, close_time=2015-03-04 18:30:00, open_price=175.4, close_price=173.0)",
                ],
                ["Trade(open_time=2015-03-05 14:30:00, close_time=2015-03-05 18:30:00, open_price=172.5, close_price=172.3)"],
                [
                    "Trade(open_time=2015-03-06 10:30:00, close_time=2015-03-06 11:30:00, open_price=173.1, close_price=172.2)",
                    "Trade(open_time=2015-03-06 12:00:00, close_time=2015-03-06 14:30:00, open_price=171.1, close_price=171.9)",
                    "Trade(open_time=2015-03-06 15:30:00, close_time=2015-03-06 18:30:00, open_price=171.9, close_price=170.5)",
                ],
            ],
        )


if __name__ == "__main__":
    unittest.main()
