from tester_trade_log.tester import Strategy, Tester
import datetime
import unittest


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
        t.set_interval(datetime.timedelta())
        t.set_trading_days(5)
        t.set_time_after_start(datetime.timedelta(minutes=60))
        t.set_time_before_finish(datetime.timedelta(minutes=9))
        t.set_interval(datetime.timedelta(minutes=30))

    def tick(self, t):
        self.dates.append(t.get_datetime().strftime("%Y/%m/%d %H:%M:%S"))
        self.prices.append(t.get_price())
        self.volumes.append(t.get_volume())

    def on_start(self, t):
        self.start_dates.append(t.get_datetime())

    def on_finish(self, t):
        self.finish_dates.append(t.get_datetime())


class TestTradeLog(unittest.TestCase):
    def test_trade_log(self):
        strategy = TestStrategy("TEST_TICKER")
        tester = Tester("tester_trade_log/tests", strategy)
        positions = tester.test()
        observations = [
            " ".join([str(date), str(price), str(volume)]) for date, price, volume in zip(strategy.dates, strategy.prices, strategy.volumes)
        ]
        # assert observations == []
        self.assertEqual(
            observations,
            [
                "2015/03/01 11:00:00 1.1 0",
                "2015/03/01 11:30:00 2.2 2",
                "2015/03/01 12:00:00 8.8 12",
                "2015/03/01 12:30:00 8.8 0",
                "2015/03/01 13:00:00 8.8 0",
                "2015/03/01 13:30:00 8.8 0",
                "2015/03/01 14:00:00 8.8 0",
                "2015/03/01 14:30:00 8.8 0",
                "2015/03/01 15:00:00 8.8 0",
                "2015/03/01 15:30:00 8.8 0",
                "2015/03/01 16:00:00 55.55 55",
                "2015/03/01 16:30:00 55.55 0",
                "2015/03/01 17:00:00 55.55 0",
                "2015/03/01 17:30:00 55.55 0",
                "2015/03/01 18:00:00 55.55 0",
                "2015/03/01 18:30:00 16.16 16",
                "2015/03/02 18:30:00 2.2 3",
                "2015/03/03 18:30:00 4.4 7",
                "2015/03/04 18:30:00 5.5 5",
            ],
        )


if __name__ == "__main__":
    unittest.main()
