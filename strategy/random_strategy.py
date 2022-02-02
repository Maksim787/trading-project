import datetime
import random
import math

from strategy.base import BaseStrategy


class RandomStrategy(BaseStrategy):
    def __init__(self, equity: str, cash: float, date: datetime.date = datetime.date.today()):
        self.equity: str = equity
        self.cash: float = cash
        self.date = date
        self.my_orders: list[int] = []
        self.reserved_equity = 0
        random.seed(1)

    def initialize(self, t):
        t.add_equity(self.equity)
        t.set_cash(self.cash)
        t.set_start(self.date)
        t.set_end(self.date + datetime.timedelta(days=1))
        t.set_interval("1m")

    def make_tick(self, t):
        if random.random() < 0.5:
            for order_id in self.my_orders:
                t.close_order(order_id)
            self.my_orders = []

        price = t.get_price(self.equity)
        cash = t.get_cash()
        equity_number = t.get_equity(self.equity)

        if random.random() < 0.5:
            number = int(math.floor(cash / price / 2))
        else:
            number = int(math.ceil(-equity_number / 2))
        if random.random() < 0.5:
            t.create_order(number // 2, self.equity, duration=10)
            take_profit = price * (1 + random.random() * 0.01)
            stop_loss = price * (1 - random.random() * 0.01)
            if number < 0:
                take_profit, stop_loss = stop_loss, take_profit
            t.create_order(number // 2, self.equity, take_profit=take_profit, stop_loss=stop_loss)
        else:
            order_id = t.create_order(number, self.equity)
            self.my_orders.append(order_id)
