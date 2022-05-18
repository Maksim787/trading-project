from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_simple_strategy import RSIStrategy

import os

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50

for check_crossing in [False, True]:
    for is_test in [False, True]:
        if check_crossing:
            file_name = "crossing"
        else:
            file_name = "simple"
        if is_test:
            file_name += "_test"
        else:
            file_name += "_train"

        def strategy_getter(ticker=None):
            return RSIStrategy(14, 10, start_test_index, trading_days_test, check_crossing=check_crossing)

        tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log")  # , tickers=["AFKS", "YNDX"])
        tester.test()
        folder = "tester_trade_log/strategies/results"
        tester.print_stats(
            trade_result_file=os.path.join(folder, f"trades_{file_name}.csv"),
            day_result_file=os.path.join(folder, f"days_{file_name}.csv"),
        )
