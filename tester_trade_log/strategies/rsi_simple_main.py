from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_simple_strategy import RSIStrategy

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50

folder = "tester_trade_log/strategies/results/data"

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

        tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log", file_name)  # , tickers=["AFKS", "YNDX"])
        tester.test()
        tester.print_stats(trade_result_folder=folder, day_result_folder=folder, detailed_result_folder=folder)
