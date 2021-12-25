import datetime
import matplotlib.pyplot as plt

from strategy.base import BaseStrategy


class TestResult:
    def __init__(
        self,
        capital_history: dict[str, list[float]],
        price_history: dict[str, list[float]],
        strategy: BaseStrategy,
    ):
        n_ticks = len(capital_history["money"])
        price_history["money"] = [1] * n_ticks
        self.total_capital_list = [0] * n_ticks
        for stock_name, stock_numbers in capital_history.items():
            for tick, number in enumerate(stock_numbers):
                self.total_capital_list[tick] += number * price_history[stock_name][tick]
        start = datetime.date.fromisoformat(strategy.start)
        end = datetime.date.fromisoformat(strategy.end)

    def plot_capital(self):
        plt.plot(range(len(self.total_capital_list)), self.total_capital_list)
        plt.show()
