import datetime

from typing import Union
from heapq import *


class Order:
    id_cnt = 0

    def __init__(self, number: int, equity: str, duration: Union[int, None]):
        self.number = number
        self.equity = equity
        self.duration = duration
        self.id = Order.id_cnt
        Order.id_cnt += 1


class Tester:
    def __init__(self, data_getter, result_object):
        """
        :param data_getter: объект, который предоставляет метод get_equity
        :param result_object: объект, который предоставляет метод initialize
        """
        self.data_getter = data_getter
        self.result_object = result_object

        self.required_equities = []  # используемые equities
        self.start: datetime.date = datetime.date(2020, 1, 1)  # начало
        self.end: datetime.date = datetime.date.today()  # конец
        self.interval = "1d"  # интервал между наблюдениями

        self.orders_by_id: dict[int, Order] = {}  # ордера по id
        self.close_order_queue = []  # ордера с определенной датой погашения

        self.current_price_history: dict[str, list[float]] = {}  # текущая история цен по названию equity
        self.current_capital: dict[str, float] = {"cash": 0.0}  # текущие количества equity и cash
        self.current_tick: int = 0  # текущий tick

        self.all_price_history: dict[str, list[float]] = {}  # вся история цен по названию equity
        self.capital_history: dict[str, list[float]] = {}  # история количества equity и cash по названию
        self.total_ticks: int = 0  # количество ticks

    def get_start(self) -> datetime.date:
        return self.start

    def get_end(self) -> datetime.date:
        return self.end

    def get_current_tick(self) -> int:
        return self.current_tick

    def get_total_ticks(self) -> int:
        return self.total_ticks

    def get_capital(self) -> dict[str, float]:
        return self.current_capital

    def get_capital_history(self) -> dict[str, list[float]]:
        return self.capital_history

    def get_current_prices(self):
        return {equity: price_list[-1] for equity, price_list in self.current_price_history.items()}

    def get_price_history(self):
        return self.current_price_history

    def set_start(self, start: datetime.date):
        self.start = start

    def set_end(self, end: datetime.date):
        self.end = end

    def set_interval(self, interval: str):
        """
        :param interval: интервал между наблюдениями: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        :return:
        """
        self.interval = interval

    def add_equity(self, equity: str):
        self.required_equities.append(equity)

    def set_cash(self, cash: Union[int, float]):
        self.current_capital["cash"] = float(cash)

    def create_order(self, number: int, equity: str, duration=None) -> int:
        """
        Создает новый Order

        :param number: количество инструмента (положительное - покупка, отрицательное - продажа)
        :param equity: название инструмента
        :param duration: продолжительность позиции, если указана
        :return: order_id - идентификатор позиции
        """
        order = Order(number, equity, duration)
        self.orders_by_id[order.id] = order
        self.change_capital(order, +1)
        if duration is not None:
            heappush(self.close_order_queue, (self.get_current_tick() + duration, order.id))
        return order.id

    def close_order(self, order_id: int):
        """
        Закрывает Order с order_id

        :param order_id:
        :return:
        """
        order = self.orders_by_id.pop(order_id)
        self.change_capital(order, -1)

    def close_all_orders(self):
        while self.orders_by_id:
            order_id, order = self.orders_by_id.popitem()
            self.change_capital(order, -1)

    def test(self, strategy):
        """
        Тестирует стратегию

        :param strategy: стратегия для тестирования
        :return:
        """
        strategy.initialize(self)  # получаем настройки стратегии

        self.initialize_data()  # загружаем данные
        for tick in range(self.total_ticks):
            self.add_price_history(tick)  # добавляем цены в историю
            self.record_capital()  # записываем капитал
            self.close_duration_orders()  # закрываем ордера с duration
            strategy.make_tick(self)  # стратегия делает ход
        self.result_object.initialize(self.capital_history, self.all_price_history, self)
        return self.result_object

    def reset(self):
        """
        Заново зовет конструктор с теми же параметрами
        """
        self.__init__(self.data_getter, self.result_object)

    def initialize_data(self):
        total_ticks = None
        for equity in self.required_equities:
            if equity not in self.all_price_history:
                equity_history = self.data_getter.get_equity(equity, start=self.start, end=self.end, interval=self.interval)
                if total_ticks is None:
                    total_ticks = len(equity_history)
                elif total_ticks != len(equity_history):
                    raise RuntimeError(
                        f"{equity} do not have the same number of ticks. total_ticks={total_ticks}. len(equity_history) = {len(equity_history)}"
                    )
                self.all_price_history[equity] = equity_history
                self.current_price_history[equity] = []
                self.current_capital[equity] = 0
                self.capital_history[equity] = []
        self.total_ticks = total_ticks
        self.capital_history["cash"] = []

    def add_price_history(self, tick):
        self.current_tick = tick
        for stock_name, price_list in self.all_price_history.items():
            self.current_price_history[stock_name].append(price_list[tick])

    def record_capital(self):
        for equity, number in self.current_capital.items():
            self.capital_history[equity].append(number)

    def close_duration_orders(self):
        current_tick = self.get_current_tick()
        while self.close_order_queue and self.close_order_queue[0][0] == current_tick:
            tick, order_id = heappop(self.close_order_queue)
            if order_id in self.orders_by_id:
                self.close_order(order_id)

    def change_capital(self, order: Order, is_open: int):
        #           +1, если открыт
        # is_open =
        #           -1, если закрыт
        cash = order.number * self.current_price_history[order.equity][-1]
        self.current_capital["cash"] -= is_open * cash
        self.current_capital[order.equity] += is_open * order.number
