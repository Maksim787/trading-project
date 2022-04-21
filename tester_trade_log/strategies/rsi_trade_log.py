from tester_trade_log.strategies.rsi import RSIStrategy
from tester_trade_log.tester import Tester
from tester_trade_log.stats import print_stats

import matplotlib.pyplot as plt

strategy = RSIStrategy("AFKS", 14, 0, 125)
tester = Tester("analysis/data/tickers_trade_log", strategy)
tester.test()
print_stats(tester)
plt.title(f"RSI, {tester.get_days()[0]}")
plt.plot(strategy.rsi_history[0])
plt.show()
