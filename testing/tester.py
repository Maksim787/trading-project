import datetime

from typing import Union
from heapq import *


class Order:
    id_cnt = 0

    def __init__(self, number: int, equity: str, duration: Union[int, None]):
        """

        :param number: количество для покупки (отрицательное для продажи)
        :param equity: название актива
        :param duration: количество периодов, через которое позиция будет автоматически закрыта
        """
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

    def set_start(self, start: datetime.date):
        """
        установить дату начала работы стратегии

        :param start: дата начала
        """
        self.start = start

    def set_end(self, end: datetime.date):
        """
        установить дату окончания работы стратегии

        :param end: дата окончания
        """
        self.end = end

    def set_interval(self, interval: str):
        """
        установить частоту, на которой будет работать стратегия

        :param interval: интервал между наблюдениями цен: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        self.interval = interval

    def set_cash(self, cash: Union[int, float]):
        """
        установить начальное количество денег

        :param cash: количество денег
        """
        self.current_capital["cash"] = float(cash)

    def add_equity(self, equity: str):
        """
        добавить слежение за ценами актива

        :param equity: название актива
        """
        self.required_equities.append(equity)

    def get_start(self) -> datetime.date:
        """
        :return: дата начала работы стратегии
        """
        return self.start

    def get_end(self) -> datetime.date:
        """
        :return: дата конца работы стратегии
        """
        return self.end

    def get_tick(self) -> int:
        """
        :return: номер текущего периода
        """
        return self.current_tick

    def get_total_ticks(self) -> int:
        """
        :return: общее количество периодов, в которые тестируется стратегия
        """
        return self.total_ticks

    def get_cash(self) -> float:
        """
        :return: количество денег на текущий момент
        """
        return self.current_capital["cash"]

    def get_equity(self, equity: str) -> float:
        """
        :param equity: название актива
        :return: количество актива на данный момент
        """
        return self.current_capital[equity]

    def get_capital(self) -> dict[str, float]:
        """
        :return: количество всех активов на текущий момент
        """
        return self.current_capital.copy()

    def get_price(self, equity: str) -> float:
        """
        :param equity: название актива
        :return: цена актива на текущий момент
        """
        return self.current_price_history[equity][-1]

    def get_prices(self) -> dict[str, float]:
        """
        :return: цены на все активы
        """
        return {equity: price_list[-1] for equity, price_list in self.current_price_history.items()}

    def get_capital_history(self) -> dict[str, list[float]]:
        """
        :return: история количества всех активов (нельзя менять, автоматически дополняется каждый период)
        """
        return self.capital_history

    def get_equity_price_history(self, equity: str) -> list[float]:
        """
        :param equity: название актива
        :return: история цен актива
        """
        return self.current_price_history[equity]

    def get_price_history(self) -> dict[str, list[float]]:
        """
        :return: история цен всех активов (нельзя менять, автоматически дополняется каждый период)
        """
        return self.current_price_history

    def get_order(self, order_id: int) -> Order:
        """
        :param order_id: id созданной ранее позиции
        :return: объект класса Order, соответствующий позиции (нельзя менять)
        """
        return self.orders_by_id[order_id]

    def buy_equity(self, number: int, equity: str):
        """
        купить актив

        :param number: количество для покупки (отрицательное для продажи)
        :param equity: название актива
        """
        self._change_capital(number, equity)

    def sell_equity(self, number: int, equity: str):
        """
        продать актив

        :param number: количество для продажи (отрицательное для покупки)
        :param equity: название актива
        """
        self._change_capital(-number, equity)

    def create_order(self, number: int, equity: str, duration=None) -> int:
        """
        создает новый Order - позицию, за которой можно следить

        :param number: количество актива (положительное - покупка, отрицательное - продажа)
        :param equity: название актива
        :param duration: продолжительность позиции, если указана
        :return: order_id - уникальный идентификатор позиции
        """
        order = Order(number, equity, duration)
        self.orders_by_id[order.id] = order
        self._change_capital(order.number, order.equity)
        if duration is not None:
            heappush(self.close_order_queue, (self.get_tick() + duration, order.id))
        return order.id

    def close_order(self, order_id: int):
        """
        закрывает Order с order_id

        :param order_id: id созданной ранее позиции
        :return:
        """
        order = self.orders_by_id.pop(order_id)
        self._change_capital(-order.number, order.equity)

    def close_all_orders(self):
        """
        закрывает все позиции
        """
        while self.orders_by_id:
            order_id, order = self.orders_by_id.popitem()
            self._change_capital(-order.number, order.equity)

    def test(self, strategy):
        """
        тестирует стратегию

        :param strategy: объект наследника класса BaseStrategy для тестирования
        :return:
        """
        strategy.initialize(self)  # получаем настройки стратегии

        self._initialize_data()  # загружаем данные
        for tick in range(self.total_ticks):
            self._add_price_history(tick)  # добавляем цены в историю
            self._record_capital()  # записываем капитал
            self._close_duration_orders()  # закрываем ордера с duration
            strategy.make_tick(self)  # стратегия делает ход
        self.result_object.initialize(self.capital_history, self.all_price_history, self)
        return self.result_object

    def _initialize_data(self):
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

    def _add_price_history(self, tick):
        self.current_tick = tick
        for stock_name, price_list in self.all_price_history.items():
            self.current_price_history[stock_name].append(price_list[tick])

    def _record_capital(self):
        for equity, number in self.current_capital.items():
            self.capital_history[equity].append(number)

    def _close_duration_orders(self):
        current_tick = self.get_tick()
        while self.close_order_queue and self.close_order_queue[0][0] == current_tick:
            tick, order_id = heappop(self.close_order_queue)
            if order_id in self.orders_by_id:
                self.close_order(order_id)

    def _change_capital(self, number: int, equity: str):
        """
        :param number: +x, если покупка x; -x, если продажа x
        :param equity:
        :return:
        """
        cash = number * self.current_price_history[equity][-1]
        self.current_capital["cash"] -= cash
        self.current_capital[equity] += number
