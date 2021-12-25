import datetime

from typing import Union
from heapq import *


class Order:
    id_cnt = 0

    def __init__(self, strategy, stock_name, is_buy, number, duration):
        self.strategy = strategy
        self.stock_name = stock_name
        self.is_buy = is_buy
        self.number = number
        self.duration = duration
        self.id = Order.id_cnt
        Order.id_cnt += 1
        if duration is not None:
            heappush(self.strategy.close_order_queue, (self.strategy.tick + duration, self.id))

    def close(self):
        self.strategy.closed_orders.append(self.id)


class BaseStrategy:
    name = ""

    def __init__(self, initial_money=1e6):
        # change, use
        self.needed_stocks = []
        self.start = "2020-01-01"
        self.end = datetime.date.today().isoformat()
        self.interval = "1d"

        # not change, use
        self.orders: dict[int, Order] = {}
        self.price_history: dict[str, list[float]] = {}
        self.capital: dict[str, float] = {"money": initial_money}
        self.tick = 0

        # not change, not use
        self.new_orders = []
        self.closed_orders = []
        self.close_order_queue = []

    def create_order(self, stock_name: str, is_buy: Union[bool, int], number: int, duration=None):
        self.new_orders.append(Order(self, stock_name, bool(is_buy), number, duration))

    def make_tick(self) -> Union[Order, None]:
        raise NotImplementedError


if __name__ == "__main__":
    s = BaseStrategy()
