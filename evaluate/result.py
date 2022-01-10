import matplotlib.pyplot as plt

import testing.tester as tester_module


class TestResult:
    def __init__(self):
        self.total_capital_list = None
        self.capital_history = None
        self.total_ticks = None

    def initialize(self, capital_history: dict[str, list[float]], price_history: dict[str, list[float]], tester: tester_module.Tester):
        self.total_ticks = tester.get_total_ticks()
        self.capital_history = capital_history.copy()
        price_history["cash"] = [1] * self.total_ticks
        self.total_capital_list = [0] * self.total_ticks
        for equity, equity_numbers in capital_history.items():
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

        for equity, equity_numbers in self.capital_history.items():
            plt.plot(range(self.total_ticks), equity_numbers)
            plt.title(f"Количество {equity} в портфеле")
            plt.xlabel("Число прошедших периодов")
            plt.ylabel("Капитал в % от начального")
            plt.show()
