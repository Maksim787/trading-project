from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_strategy import RSIStrategy

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50


def strategy_getter(ticker=None):
    return RSIStrategy(14, 10, start_test_index, trading_days_test)


tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log")  # , tickers=["AFKS", "YNDX"])
tester.test()
tester.print_stats()
