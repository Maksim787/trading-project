from data.getter import DataGetter
from strategy.base import BaseStrategy

from typing import Union
from heapq import *


class Tester:
    def __init__(self, data_getter: DataGetter, result_class):
        self.data_getter: DataGetter = data_getter
        self.result_class = result_class
        self.data: dict[str, list[float]] = {}
        self.price_history: dict[str, list[float]] = {}
        self.n_ticks = 0
        self.tick = 0
        self.strategy: Union[None, BaseStrategy] = None
        self.capital_history: dict[str, list[float]] = {}
        self.result = None

    def test(self, strategy: BaseStrategy):
        self.strategy = strategy
        self.strategy.price_history = self.price_history
        self.init_data()
        for tick in range(self.n_ticks):
            self.tick = tick
            self.strategy.tick = tick
            self.add_price_history()
            self.strategy.make_tick()
            self.close_orders()
            self.open_orders()
            self.record_capital()
        return self.result_class(self.capital_history, self.price_history, self.strategy)

    def reset(self):
        self.__init__(self.data_getter, self.result_class)

    def init_data(self):
        for stock_name in self.strategy.needed_stocks:
            if stock_name not in self.data:
                self.data[stock_name] = self.data_getter.get_stock(
                    stock_name,
                    start=self.strategy.start,
                    end=self.strategy.end,
                    interval=self.strategy.interval,
                )
                self.price_history[stock_name] = []
                self.strategy.capital[stock_name] = 0
                self.capital_history[stock_name] = []
                self.n_ticks = len(self.data[stock_name])
        self.capital_history["money"] = []

    def add_price_history(self):
        for stock_name, price_list in self.data.items():
            self.price_history[stock_name].append(price_list[self.tick])
        self.strategy.tick = self.tick

    def record_capital(self):
        for stock_name, number in self.strategy.capital.items():
            self.capital_history[stock_name].append(number)

    def change_capital(self, order, is_open):
        sign = (order.is_buy * 2 - 1) * (is_open * 2 - 1)
        money = order.number * self.price_history[order.stock_name][-1]
        self.strategy.capital["money"] -= sign * money
        self.strategy.capital[order.stock_name] += sign * order.number

    def close_orders(self):
        while (
            self.strategy.close_order_queue and self.strategy.close_order_queue[0][0] == self.tick
        ):
            (tick, order_id) = heappop(self.strategy.close_order_queue)
            self.strategy.orders[order_id].close()
        for order_id in self.strategy.closed_orders:
            order = self.strategy.orders.pop(order_id)
            self.change_capital(order, False)
        self.strategy.closed_orders = []

    def open_orders(self):
        for order in self.strategy.new_orders:
            self.change_capital(order, True)
            self.strategy.orders[order.id] = order
        self.strategy.new_orders = []
