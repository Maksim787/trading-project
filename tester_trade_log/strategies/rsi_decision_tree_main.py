from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_decision_tree import RSITreeStrategy

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50


def strategy_getter(ticker):
    return RSITreeStrategy(ticker, start_test_index, trading_days_test, 10)


tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log")
tester.test()
tester.print_stats()
