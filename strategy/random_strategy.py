import datetime
import random
import math

from strategy.base import BaseStrategy


class RandomStrategy(BaseStrategy):
    def __init__(self, equity: str, cash: float):
        super().__init__()
        self.equity: str = equity
        self.cash: float = cash
        self.my_orders: list[int] = []
        random.seed(1)

    def initialize(self):
        t = self.tester
        t.add_equity(self.equity)
        t.set_cash(self.cash)
        t.set_start(datetime.date(2020, 1, 1))
        t.set_end(datetime.date.today())
        t.set_interval("1d")

    def make_tick(self):
        t = self.tester

        if random.random() < 0.5:
            for order_id in self.my_orders:
                t.close_order(order_id)
            self.my_orders = []

        capital = t.get_capital()
        price = t.get_current_prices()[self.equity]
        cash = capital["cash"]
        equity_number = capital[self.equity]

        is_buy = random.choice([1, -1])
        if is_buy == 1:
            number = int(math.floor(cash / 2 / price))
        else:
            number = -equity_number // 2
        if random.random() < 0.5:
            t.create_order(number, self.equity, duration=10)
        else:
            order_id = t.create_order(number, self.equity)
            self.my_orders.append(order_id)
