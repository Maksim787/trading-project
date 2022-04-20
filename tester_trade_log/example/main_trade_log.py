from tester_trade_log.tester import Tester
from tester_trade_log.example.example_strategy import ExampleStrategy
import matplotlib.pyplot as plt
import numpy as np


def print_stats(days, trades_by_days):
    returns_by_day = []
    for day, trades in zip(days, trades_by_days):
        returns = [trade.close_price / trade.open_price for trade in trades]
        returns_by_day.append(np.product(returns))
    plt.plot(np.cumprod(returns_by_day))
    plt.show()


def main():
    tester = Tester("analysis/data/tickers_trade_log", ExampleStrategy("AFKS"))
    days, trades_by_days = tester.test()
    print_stats(days, trades_by_days)


if __name__ == "__main__":
    main()
