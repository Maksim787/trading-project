import matplotlib.pyplot as plt

import testing.tester as t


class TestResult:
    def __init__(self):
        self.total_capital_list = None
        self.total_ticks = None

    def initialize(self, capital_history: dict[str, list[float]], price_history: dict[str, list[float]], tester: t.Tester):
        self.total_ticks = tester.get_total_ticks()
        price_history["cash"] = [1] * self.total_ticks
        self.total_capital_list = [0] * self.total_ticks
        for equity, equity_numbers in capital_history.items():
            equity_prices = price_history[equity]
            for tick, number in enumerate(equity_numbers):
                self.total_capital_list[tick] += number * equity_prices[tick]

    def plot_capital(self):
        plt.plot(range(self.total_ticks), self.total_capital_list)
        plt.show()
