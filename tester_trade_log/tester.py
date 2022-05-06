import datetime
from typing import Union
from tqdm import tqdm
from tester_trade_log.data_iterator import DataIterator
from tester_trade_log.constants import EXCHANGE_CLOSE, DIRECTION


class Strategy:
    def initialize(self, t: "Tester"):
        """
        Выставляет параметры стратегии

        :param t:
        :return:
        """
        raise NotImplementedError

    def on_tick(self, t: "Tester"):
        """
        Принимает торговые решения

        :param t:
        :return:
        """
        raise NotImplementedError

    def on_start(self, t: "Tester"):
        """
        Вызывается в начале торгового дня

        :param t:
        :return:
        """
        raise NotImplementedError

    def on_finish(self, t: "Tester"):
        """
        Вызывается в конце торгового дня

        :param t:
        :return:
        """
        raise NotImplementedError


def _add_time(time: datetime.time, timedelta: datetime.timedelta):
    return (datetime.datetime.combine(datetime.date(1, 1, 1), time) + timedelta).time()


def _subtract_time(time: datetime.time, timedelta: datetime.timedelta):
    return (datetime.datetime.combine(datetime.date(1, 1, 1), time) - timedelta).time()


class Trade:
    def __init__(self, open_time: datetime.datetime, close_time: datetime.datetime, open_price: float, close_price: float, direction: DIRECTION):
        self.open_time: datetime.datetime = open_time
        self.close_time: datetime.datetime = close_time
        self.open_price: float = open_price
        self.close_price: float = close_price
        self.direction = direction

    def _close(self, close_time: datetime.datetime, close_price: float):
        self.close_time = close_time
        self.close_price = close_price

    def profit_ratio(self):
        """
        Возвращает коэффициент, на который умножается капитал, вложенный в сделку

        :return:
        """
        return 1 + (self.close_price - self.open_price) * self.direction.value / self.open_price

    def __repr__(self):
        return f"Trade(open_time={self.open_time}, close_time={self.close_time}, open_price={self.open_price}, close_price={self.close_price})"


class OpenPosition:
    def __init__(
        self,
        open_time: datetime.datetime,
        interval: datetime.timedelta,
        open_price: float,
        direction: DIRECTION,
        duration: Union[int, None],
        take_profit: Union[float, None],
        stop_loss: Union[float, None],
    ):
        self.open_time = open_time
        self.open_price = open_price
        self.direction = direction
        self.expected_close = open_time + interval * duration if duration is not None else None
        self.take_profit = take_profit if take_profit is not None else float("+inf") * direction.value
        self.stop_loss = stop_loss if stop_loss is not None else float("-inf") * direction.value

    def check_close(self, price: float, current_time: datetime.datetime) -> bool:
        if (price - self.take_profit) * self.direction.value >= 0:
            return True
        if (price - self.stop_loss) * self.direction.value <= 0:
            return True
        if self.expected_close is not None and current_time >= self.expected_close:
            return True
        return False

    def close(self, close_time: datetime.datetime, close_price: float) -> Trade:
        return Trade(self.open_time, close_time, self.open_price, close_price, self.direction)


class Tester:
    def __init__(self, data_directory: str, strategy: Strategy):
        """

        :param data_directory: директория с данными
        :param strategy:
        """
        self._data_directory = data_directory
        self._strategy = strategy
        self._ticker = ""

        # time
        self._start_day_index = 0
        self._trading_days = 0
        self._interval = datetime.timedelta()
        self._intervals_after_start = 0
        self._finish_time = EXCHANGE_CLOSE

        # current values
        self._current_time: Union[datetime.datetime, None] = None
        self._current_price: Union[float, None] = None
        self._current_volume: Union[int, None] = None

        # today history values
        self._price_history: list[float] = []
        self._volume_history: list[int] = []

        # day history values
        self._day_close_price_history: list[float] = []
        self._days_history: list[datetime.date] = []
        self._trades_history: list[list[Trade]] = []

        # position
        self._position: Union[OpenPosition, None] = None

    def test(self, show_progress=True):
        self._strategy.initialize(self)  # initialize strategy
        assert self._ticker and self._interval
        with DataIterator(self._data_directory, self._ticker, self._interval) as data_iterator:
            data_iterator = enumerate(data_iterator)
            if show_progress:
                data_iterator = tqdm(data_iterator)
            for day_index, (day, intraday_iterator) in data_iterator:
                if day_index < self._start_day_index:
                    continue
                if day_index >= self._start_day_index + self._trading_days:
                    break
                self._days_history.append(day)
                self._trades_history.append([])
                started = False
                for time, price, volume in intraday_iterator:
                    if time.time() > self._finish_time:
                        break
                    self._current_time = time
                    self._current_price = price
                    self._current_volume = volume
                    self._price_history.append(price)
                    self._volume_history.append(volume)
                    if not started and len(self._price_history) >= self._intervals_after_start:
                        self._strategy.on_start(self)
                        started = True
                    if started:
                        self._on_tick()
                self._on_finish_day()

    # strategy.initialize()

    def set_ticker(self, ticker: str):
        self._ticker = ticker

    def set_interval(self, interval: datetime.timedelta):
        self._interval = interval

    def set_start_day_index(self, day_index: int):
        self._start_day_index = day_index

    def set_trading_days(self, days: int):
        self._trading_days = days

    def set_intervals_after_start(self, n_intervals: int):
        self._intervals_after_start = n_intervals

    def set_intervals_before_finish(self, n_intervals: int):
        self._finish_time = _subtract_time(EXCHANGE_CLOSE, n_intervals * self._interval)

    # strategy.on_tick()

    # current values
    def get_current_time(self) -> datetime.datetime:
        return self._current_time

    def get_current_price(self) -> float:
        return self._current_price

    def get_current_volume(self) -> int:
        return self._current_volume

    # today history values
    def get_today_price_history(self) -> list[float]:
        return self._price_history

    def get_today_volume_history(self) -> list[int]:
        return self._volume_history

    # position handling
    def is_open_position(self) -> bool:
        return self._position is not None

    def buy(
        self,
        duration: Union[None, int] = None,
        take_profit: Union[float, None] = None,
        stop_loss: Union[float, None] = None,
    ):
        self.open_position(DIRECTION.LONG, duration, take_profit, stop_loss)

    def sell(
        self,
        duration: Union[None, int] = None,
        take_profit: Union[float, None] = None,
        stop_loss: Union[float, None] = None,
    ):
        self.open_position(DIRECTION.SHORT, duration, take_profit, stop_loss)

    def open_position(
        self, direction, duration: Union[None, int] = None, take_profit: Union[float, None] = None, stop_loss: Union[float, None] = None
    ):
        if self._position is not None:
            if self._position.direction == direction:
                return
            else:
                self.close_position()
        self._position = OpenPosition(self._current_time, self._interval, self._current_price, DIRECTION.LONG, duration, take_profit, stop_loss)

    def close_position(self):
        if self._position is None:
            return
        self._trades_history[-1].append(self._position.close(self._current_time, self._current_price))
        self._position = None

    # general information
    def get_day_close_price_history(self) -> list[float]:
        return self._day_close_price_history

    def get_trades_history(self) -> list[list[Trade]]:
        return self._trades_history

    def get_days_history(self) -> list[datetime.date]:
        return self._days_history

    def get_ticker(self) -> str:
        return self._ticker

    # utility functions
    def _on_finish_day(self):
        self._strategy.on_finish(self)
        if self.is_open_position():
            self.close_position()
        self._day_close_price_history.append(self._current_price)
        self._price_history.clear()
        self._volume_history.clear()

    def _on_tick(self):
        if self._position is not None:
            if self._position.check_close(self._current_price, self._current_time):
                self.close_position()
        self._strategy.on_tick(self)