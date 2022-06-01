from tester_trade_log.stats import StrategyTester
from tester_trade_log.strategies.rsi_decision_tree import RSITreeStrategy

import os

start_train_index = 0
trading_days_train = 199

start_test_index = 199
trading_days_test = 50

folder = "tester_trade_log/strategies/results/data"

for model_name in ["tree", "forest"]:
    for probability_distance in [0, 0.01, 0.02, 0.05]:
        model_path = os.path.join("tester_trade_log/models/saved", model_name)

        def strategy_getter(ticker):
            return RSITreeStrategy(ticker, start_test_index, trading_days_test, 10, model_path, probability_distance)

        tester = StrategyTester(strategy_getter, "analysis/data/tickers_trade_log", f"{model_name}_{probability_distance}")
        tester.test()
        tester.print_stats(trade_result_folder=folder, day_result_folder=folder, detailed_result_folder=folder)
