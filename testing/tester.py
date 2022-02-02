import datetime

from typing import Union
from heapq import *


class Order:
    id_cnt = 0

    def __init__(self, number: int, equity: str,
                 take_profit: Union[float, None],
                 stop_loss: Union[float, None],
                 duration: Union[int, None]):
        self.number = number
        self.equity = equity
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.duration = duration
        self.id = Order.id_cnt
        Order.id_cnt += 1


class Tester:
    def __init__(self, data_getter, result_objects):
        """
        :param data_getter: объект, который предоставляет метод get_equity
        :param result_objects: объекты класса, наследуемого от BaseResult
        """
        self.data_getter = data_getter
        self.result_objects = result_objects

        self.required_equities = []  # используемые equities
        self.start: datetime.date = datetime.date(2020, 1, 1)  # начало
        self.end: datetime.date = datetime.date.today()  # конец
        self.interval = "1d"  # интервал между наблюдениями

        self.orders_by_id: dict[int, Order] = {}  # ордера по id
        self.duration_order_queue: list[tuple[int, int]] = []  # heap (close_tick, order_id)
        self.take_profit_order_queue: dict[str, list[tuple[float, int]]] = {}  # min heap by price: (price, order_id)
        self.stop_loss_order_queue: dict[str, list[tuple[float, int]]] = {}  # max heap by price: (-price, order_id)

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

    def create_order(self, number: int, equity: str,
                     take_profit: Union[float, None] = None, stop_loss: Union[float, None] = None,
                     duration: Union[int, None] = None) -> int:
        """
        создает новый Order - позицию, за которой можно следить

        :param number: количество актива (положительное - покупка, отрицательное - продажа)
        :param equity: название актива
        :param take_profit: цена, при достижении которой нужно зафиксировать прибыль
        :param stop_loss: цена, при достижении которой нужно зафиксировать убыток
        :param duration: количество периодов, через которое позиция будет автоматически закрыта
        :return: order_id - уникальный идентификатор позиции
        """
        order = Order(number, equity, take_profit, stop_loss, duration)
        self.orders_by_id[order.id] = order
        self._change_capital(order.number, order.equity)
        if number < 0:
            # если происходит продажа, то нижняя граница становится take_profit, а верхняя stop_loss
            take_profit, stop_loss = stop_loss, take_profit
        price = self.get_price(equity)
        if take_profit is not None:
            assert price < take_profit, f"Strange order: {order.number = }, {order.take_profit = }, {price = }"
        if stop_loss is not None:
            assert price > stop_loss, f"Strange order: {order.number = }, {order.stop_loss = }, {price = }"

        if duration is not None:
            heappush(self.duration_order_queue, (self.get_tick() + duration, order.id))
        if take_profit is not None:
            heappush(self.take_profit_order_queue.setdefault(equity, []), (take_profit, order.id))
        if stop_loss is not None:
            heappush(self.stop_loss_order_queue.setdefault(equity, []), (-stop_loss, order.id))
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
            self._close_orders()  # закрываем ордера с duration, take_profit, stop_loss
            strategy.make_tick(self)  # стратегия делает ход
        for result_object in self.result_objects:
            result_object.initialize(self)
        return self.result_objects

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

    def _close_orders(self):
        # close duration orders
        current_tick = self.get_tick()
        while self.duration_order_queue and self.duration_order_queue[0][0] == current_tick:
            order_id = heappop(self.duration_order_queue)[1]
            if order_id in self.orders_by_id:
                self.close_order(order_id)
        # close take_profit orders
        for equity, queue in self.take_profit_order_queue.items():
            price = self.get_price(equity)
            while queue and queue[0][0] <= price:
                order_id = heappop(queue)[1]
                if order_id in self.orders_by_id:
                    self.close_order(order_id)
        # close stop_loss orders
        for equity, queue in self.stop_loss_order_queue.items():
            price = self.get_price(equity)
            while queue and -queue[0][0] >= price:
                order_id = heappop(queue)[1]
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
