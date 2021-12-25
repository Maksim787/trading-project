import datetime
import random
import math

from strategy.base import BaseStrategy


class RandomStrategy(BaseStrategy):
    def __init__(self, stock_name, initial_money=1e6):
        super().__init__(initial_money)
        self.stock_name = stock_name
        self.needed_stocks.append(stock_name)
        self.start = "2020-01-01"
        self.end = datetime.date.today().isoformat()
        self.interval = "1d"

    def make_tick(self):
        money = self.capital["money"]
        stock = self.capital[self.stock_name]
        is_buy = random.randint(0, 1)
        number = stock // 2
        if is_buy:
            number = int(math.floor(money // self.price_history[self.stock_name][-1]))
        self.create_order(self.stock_name, is_buy, number, 10)
