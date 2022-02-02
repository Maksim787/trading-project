import matplotlib.pyplot as plt

from result.base import BaseResult


class CapitalResult(BaseResult):
    def __init__(self, plot_equity_number=False):
        self.plot_equity_number = plot_equity_number
        self.total_ticks = 0
        self.capital_history = {}
        self.total_capital_list = []

    def initialize(self, t):
        self.total_ticks = t.get_total_ticks()
        self.capital_history = t.get_capital_history().copy()
        price_history = t.get_price_history()
        price_history["cash"] = [1] * self.total_ticks
        self.total_capital_list = [0] * self.total_ticks
        for equity, equity_numbers in self.capital_history.items():
            equity_prices = price_history[equity]
            for tick, number in enumerate(equity_numbers):
                self.total_capital_list[tick] += number * equity_prices[tick]
        self.total_capital_list = list(map(lambda x: x * 100 / self.total_capital_list[0], self.total_capital_list))

    def plot_capital(self):
        plt.plot(range(self.total_ticks), self.total_capital_list)
        plt.title("Стоимость портфеля")
        plt.xlabel("Число прошедших периодов")
        plt.ylabel("Капитал в % от начального")
        plt.show()
        if self.plot_equity_number:
            for equity, equity_numbers in self.capital_history.items():
                plt.plot(range(self.total_ticks), equity_numbers)
                plt.title(f"Количество {equity} в портфеле")
                plt.xlabel("Число прошедших периодов")
                plt.ylabel("Капитал в % от начального")
                plt.show()
