from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_decision_tree import RSITreeStrategy

import os

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50

model_name = "tree"

for probability_distance in [0, 0.05]:
    model_path = os.path.join("tester_trade_log/models/saved", model_name)

    def strategy_getter(ticker):
        return RSITreeStrategy(ticker, start_test_index, trading_days_test, 10, model_path, probability_distance)

    tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log")
    tester.test()
    folder = "tester_trade_log/strategies/results"
    tester.print_stats(
        trade_result_file=os.path.join(folder, f"trades_{model_name}_{probability_distance}.csv"),
        day_result_file=os.path.join(folder, f"days_{model_name}_{probability_distance}.csv"),
    )
