import numpy as np
from tester_trade_log.tester import Tester
import matplotlib.pyplot as plt


def print_stats(tester: Tester):
    returns_by_day = []
    days = tester.get_days()
    trades_history = tester.get_trades_history()
    for day, trades in zip(days, trades_history):
        returns = [trade.close_price / trade.open_price for trade in trades]
        returns_by_day.append(np.product(returns))
    close_prices = np.array(tester.get_day_close_prices())
    plt.plot(days, close_prices / close_prices[0], label="Цена акции")
    plt.plot(days, np.cumprod(returns_by_day), label="Капитал стратегии")
    plt.legend()
    plt.title(f"{tester.get_ticker()}")
    plt.xlabel(f"{len(days)} рабочих дней")
    plt.show()
