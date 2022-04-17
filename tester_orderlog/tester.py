import csv
import datetime
from enum import Enum
from sortedcontainers import SortedSet


class Direction(Enum):
    Buy = 0
    Sell = 1


class Action(Enum):
    Withdraw = 0
    Place = 1
    Trade = 2


EXCHANGE_OPEN = datetime.time(hour=10, minute=0, second=0)
EXCHANGE_CLOSE = datetime.time(hour=18, minute=45, second=0)


class Strategy:
    def initialize(self, t: "Tester"):
        raise NotImplementedError

    def tick(self, t: "Tester"):
        raise NotImplementedError


class Order:
    def __init__(self, direction: Direction, price: float, volume: int, orderno: int):
        # strategy has orderno = -1
        self.price = price
        self.direction = direction
        self.volume = volume
        self.orderno = orderno

    def copy(self):
        raise NotImplementedError
        # return Order(self.direction, self.price, self.volume, self.orderno)

    def __repr__(self):
        return f"Order(price={self.price}, direction={self.direction}, volume={self.volume}, orderno={self.orderno})"


class Tester:
    def __init__(self, data_directory, strategy: Strategy):
        self._data_directory = data_directory
        self._strategy = strategy
        self._ticker = ""
        self._days = 0
        self._start_period = EXCHANGE_OPEN
        self._finish_period = EXCHANGE_CLOSE

        self._buy_queue = SortedSet(key=lambda x: (-x[0], x[1]))
        self._sell_queue = SortedSet()
        self._orders: dict[int, Order] = {}
        self._strategy_orderno = -1  # для стратегии нумеруем ордера отрицательными числами

        self._close = 0

    def test(self):
        self._strategy.initialize(self)  # initialize strategy
        assert self._ticker

        for tick in self._tick_iterator():
            # tick has list of events with the same time
            for event in tick:
                # event = [TIME, ACTION, BUYSELL, ORDERNO, PRICE, VOLUME, TRADEPRICE]
                action = event[1]
                if action == Action.Place:
                    self._place_data_limit_order(event[2], event[4], event[5], event[3])
                elif action == Action.Withdraw:
                    self._withdraw_data_limit_order(event[2], event[4], event[5], event[3])
                elif action == Action.Trade:
                    self._place_data_market_order(event[2], event[4], event[5], event[6], event[3])
            # check start_period and finish_period
            if self._start_period < tick[0][0].time() < self._finish_period:
                self._strategy.tick(self)

    # strategy.initialize()

    def set_ticker(self, ticker: str):
        self._ticker = ticker

    def set_trading_days(self, days: int):
        self._days = days

    def set_start_period(self, timedelta: datetime.timedelta):
        self._start_period = (
            datetime.datetime(year=1, month=1, day=1, hour=EXCHANGE_OPEN.hour, minute=EXCHANGE_OPEN.minute, second=EXCHANGE_OPEN.second) + timedelta
        ).time()

    def set_finish_period(self, timedelta: datetime.timedelta):
        self._finish_period = (
            datetime.datetime(year=1, month=1, day=1, hour=EXCHANGE_CLOSE.hour, minute=EXCHANGE_CLOSE.minute, second=EXCHANGE_CLOSE.second)
            + timedelta
        ).time()

    # strategy.test()

    def place_limit_order(self, direction: Direction, price: float, volume: int) -> int:
        # возвращает номер созданного ордера
        orderno = self._get_strategy_orderno()
        self._place_data_limit_order(direction, price, volume, orderno)
        self._execute_with_limit_order(direction, price, volume, orderno)
        return orderno

    def place_market_order(self, direction: Direction, volume: int):
        pass

    def withdraw_limit_order(self, orderno, volume):
        # снять volume с ордера
        # self._withdraw_limit_order(volume, orderno)
        pass

    def get_close(self) -> int:
        return self._close

    # utility functions

    def _get_strategy_orderno(self):
        self._strategy_orderno -= 1
        return self._strategy_orderno - 1

    def _execute_with_limit_order(self, direction: Direction, price: float, volume: int, orderno: int):
        queue = self._sell_queue if direction == Direction.Buy else self._buy_queue
        sign = 1 if direction == Direction.Buy else -1
        while queue and volume > 0:
            limit_price, limit_orderno = queue[0]
            if limit_price * sign > price * sign:
                return
            limit_order = self._orders[limit_orderno]
            self._place_data_market_order(direction, price, volume, limit_order.price, orderno)
            self._place_data_market_order(limit_order.direction, limit_order.price, limit_order.volume, limit_order.price, limit_order.orderno)
            volume = max(0, volume - limit_order.volume)

    def _place_data_limit_order(self, direction: Direction, price: float, volume: int, orderno: int):
        order = Order(direction, price, volume, orderno)
        self._orders[orderno] = order
        if direction == Direction.Buy:
            self._buy_queue.add((price, orderno))
        elif direction == Direction.Sell:
            self._sell_queue.add((price, orderno))

    def _withdraw_data_limit_order(self, direction: Direction, price: float, volume: int, orderno: int):
        if orderno not in self._orders:
            # ордер был закрыт с помощью нашей стратегии
            return
        order = self._orders[orderno]
        assert order.direction == direction and order.price == price
        if volume >= order.volume:
            self._orders.pop(orderno)
            if order.direction == Direction.Buy:
                self._buy_queue.remove((order.price, order.orderno))
            elif order.direction == Direction.Sell:
                self._sell_queue.remove((order.price, order.orderno))
        else:
            order.volume -= volume

    def _place_data_market_order(self, direction: Direction, price: float, volume: int, trade_price: float, orderno: int):
        self._close = trade_price
        if orderno not in self._orders:
            # ордер был закрыт с помощью нашей стратегии
            return

        order = self._orders[orderno]
        assert direction == order.direction and price == order.price
        assert volume <= order.volume
        if volume == order.volume:
            if direction == Direction.Buy:
                self._buy_queue.remove((price, orderno))
            elif direction == Direction.Sell:
                self._sell_queue.remove((price, orderno))
            self._orders.pop(orderno)
        order.volume -= volume

    # data functions

    def _tick_iterator(self):
        row_iterator = self._row_iterator()
        first_row: tuple[datetime.datetime, Action, Direction, int, float, int, float] = next(row_iterator)
        current_tick_time = first_row[0]
        current_tick = [first_row]
        for row in row_iterator:
            if row[0] != current_tick_time:
                yield current_tick
                current_tick.clear()
                current_tick_time = row[0]
            current_tick.append(row)
        yield current_tick

    def _row_iterator(self):
        # return [TIME, ACTION, BUYSELL, ORDERNO, PRICE, VOLUME, TRADEPRICE]
        with open(f"{self._data_directory}/{self._ticker}.csv", newline="") as f:
            reader = csv.reader(f)
            columns = next(reader)
            assert columns == ["NO", "SECCODE", "BUYSELL", "TIME", "ORDERNO", "ACTION", "PRICE", "VOLUME", "TRADENO", "TRADEPRICE"]
            for row in reader:
                # [NO, SECCODE, BUYSELL, TIME, ORDERNO, ACTION, PRICE, VOLUME, TRADENO, TRADEPRICE]
                yield (
                    datetime.datetime.strptime(row[3], "%Y%m%d%H%M%S%f"),
                    Action(int(row[5])),
                    Direction.Buy if row[2] == "B" else Direction.Sell,
                    int(row[4]),
                    float(row[6]),
                    int(row[7]),
                    float(row[9]) if row[5] == "2" else None,
                )
