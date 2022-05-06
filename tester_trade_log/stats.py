import numpy as np
from tester_trade_log.tester import Tester
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure


def sharpe_ratio(returns_by_day: np.array):
    mean = returns_by_day.mean()
    std = returns_by_day.std()
    return mean * 100, std * 100, mean / std


def print_stats(tester: Tester, plot=True):
    returns_by_day = []
    days = tester.get_days_history()
    trades_history = tester.get_trades_history()
    for day, trades in zip(days, trades_history):
        returns = [trade.profit_ratio() for trade in trades]
        returns_by_day.append(np.product(returns))
    close_prices = np.array(tester.get_day_close_price_history())
    fig: Figure = plt.figure()
    plt.plot(days, close_prices / close_prices[0], label="Цена акции", color="red")
    plt.plot(days, np.cumprod(returns_by_day), label="Капитал стратегии", color="green")
    plt.legend(loc="lower right")
    plt.title(f"{tester.get_ticker()}")
    plt.xlabel(f"{len(days)} рабочих дней")
    if plot:
        fig.show()
    return fig, sharpe_ratio(np.array(returns_by_day) - 1)
