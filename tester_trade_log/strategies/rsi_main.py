from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_strategy import RSIStrategy


def strategy_getter(ticker=None):
    return RSIStrategy(14, 10, 0, 199)


tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log")  # , tickers=["AFKS", "YNDX"])
tester.test()
tester.print_stats()
