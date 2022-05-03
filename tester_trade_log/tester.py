import datetime
from typing import Union
from tqdm import tqdm
import os

EXCHANGE_OPEN = datetime.time(10, 0, 0)
EXCHANGE_CLOSE = datetime.time(18, 40, 0)


class Strategy:
    def initialize(self, t: "Tester"):
        raise NotImplementedError

    def tick(self, t: "Tester"):
        raise NotImplementedError

    def on_start(self, t: "Tester"):
        raise NotImplementedError

    def on_finish(self, t: "Tester"):
        raise NotImplementedError


def _add_time(time: datetime.time, timedelta: datetime.timedelta):
    return (datetime.datetime.combine(datetime.date(1, 1, 1), time) + timedelta).time()


def _subtract_time(time: datetime.time, timedelta: datetime.timedelta):
    return (datetime.datetime.combine(datetime.date(1, 1, 1), time) - timedelta).time()


class DataIterator:
    def __init__(self, data_directory: str, ticker: str, interval: datetime.timedelta):
        self._data_directory = data_directory
        self._ticker = ticker
        self._interval: datetime.timedelta = interval

    def __iter__(self):
        return self._day_iterator

    def __enter__(self):
        cache_directory = f"{self._data_directory}/cache"
        cache_file_name = f"{self._ticker}.{self._interval.total_seconds()}.txt"
        cache_full_path = f"{cache_directory}/{cache_file_name}"
        if cache_file_name in os.listdir(cache_directory):
            self._use_cache = True
            self._day_iterator = self._get_day_iterator(self._get_row_iterator(cache_full_path))
        else:
            self._use_cache = False
            self._cache_file = open(cache_full_path, "w")
            self._day_iterator = self._get_day_iterator(self._get_row_iterator(f"{self._data_directory}/{self._ticker}.txt"))
        self._first_price_volume: Union[tuple[float, int], None] = None
        self._current_time: Union[datetime.datetime, None] = None
        self._reached_end = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._use_cache:
            for _ in self._day_iterator:
                pass
            self._cache_file.close()

    def _format_current_time(self, current_time: datetime.datetime):
        # делаем так, чтобы current_time был равен EXCHANGE_OPEN + k * _interval
        time_from_open = current_time - datetime.datetime.combine(current_time.date(), EXCHANGE_OPEN)
        return current_time - time_from_open % self._interval

    def _write_cache(self, time: datetime.datetime, price: float, volume: int):
        self._cache_file.write(f"{time.strftime('%Y%m%d%H%M%S')} {price} {volume}\n")

    def _get_day_iterator(self, row_iterator):
        # return [day, interval_iterator]
        time, price, volume = next(row_iterator)
        if not self._use_cache:
            time = self._format_current_time(time)
        self._first_price_volume = [price, volume]
        self._current_time = time
        while not self._reached_end:
            day = self._current_time.date()
            if self._use_cache:
                intraday_iterator = self._get_interval_cache_iterator(row_iterator)
            else:
                intraday_iterator = self._get_interval_iterator(row_iterator)
            yield [day, intraday_iterator]
            for _ in intraday_iterator:
                pass

    def _get_interval_cache_iterator(self, row_iterator):
        # return [time, price, volume]
        time = self._current_time
        price, volume = self._first_price_volume
        yield time, price, volume
        for time, price, volume in row_iterator:
            if time.date() != self._current_time.date():
                self._first_price_volume = [price, volume]
                self._current_time = time
                return
            yield time, price, volume
        self._reached_end = True

    def _get_interval_iterator(self, row_iterator):
        # return [time, price, volume]
        current_time = self._current_time
        current_price, current_volume = self._first_price_volume
        for time, price, volume in row_iterator:
            if time.date() != self._current_time.date():
                if current_volume:
                    data = (current_time + self._interval, current_price, current_volume)
                    self._write_cache(*data)
                    yield data
                self._first_price_volume = [price, volume]
                self._current_time = self._format_current_time(time)
                return
            while time - current_time >= self._interval:
                current_time += self._interval
                data = (current_time, current_price, current_volume)
                self._write_cache(*data)
                yield data
                current_volume = 0
            current_price = price
            current_volume += volume
        self._reached_end = True
        if current_volume:
            data = (current_time + self._interval, current_price, current_volume)
            self._write_cache(*data)
            yield data

    @staticmethod
    def _get_row_iterator(file_name):
        # return [TIME, PRICE, VOLUME]
        with open(file_name) as f:
            for row in f:
                row = row.split()
                if not row:
                    return
                yield datetime.datetime.strptime(row[0], "%Y%m%d%H%M%S"), float(row[1]), int(row[2])


class Trade:
    def __init__(self, open_time: datetime.datetime, close_time: datetime.datetime, open_price: float, close_price: float):
        self.open_time: datetime.datetime = open_time
        self.close_time: datetime.datetime = close_time
        self.open_price: float = open_price
        self.close_price: float = close_price

    def close(self, close_time: datetime.datetime, close_price: float):
        self.close_time = close_time
        self.close_price = close_price

    def __repr__(self):
        return f"Trade(open_time={self.open_time}, close_time={self.close_time}, open_price={self.open_price}, close_price={self.close_price})"


class OpenPosition:
    def __init__(
        self,
        open_time: datetime.datetime,
        interval: datetime.timedelta,
        open_price: float,
        duration: Union[int, None],
        keep_silent_duration: bool,
        take_profit: Union[float, None],
        stop_loss: Union[float, None],
    ):
        self.open_time = open_time
        self.open_price = open_price
        self.keep_silent_duration = keep_silent_duration
        if duration is not None:
            self.expected_close = open_time + interval * duration
        else:
            self.expected_close = None
        if take_profit is not None:
            self.take_profit = take_profit
        else:
            self.take_profit = float("+inf")
        if stop_loss is not None:
            self.stop_loss = stop_loss
        else:
            self.stop_loss = float("-inf")

    def close(self, close_time: datetime.datetime, close_price: float) -> Trade:
        return Trade(self.open_time, close_time, self.open_price, close_price)


class Tester:
    def __init__(self, data_directory: str, strategy: Strategy):
        self._data_directory = data_directory
        self._strategy = strategy
        self._ticker = ""
        self._start_day_index = 0
        self._trading_days = 0
        self._interval = datetime.timedelta()
        self._intervals_after_start = 0
        self._finish_time = EXCHANGE_CLOSE

        self._datetime: Union[datetime.datetime, None] = None
        self._price: Union[float, None] = None
        self._volume: Union[int, None] = None
        self._prices = []
        self._day_close_prices = []
        self._days: list[datetime.datetime] = []

        self._position: Union[OpenPosition, None] = None
        self._trades_history: list[list[Trade]] = []

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
                self._days.append(day)
                self._trades_history.append([])
                started = False
                for time, price, volume in intraday_iterator:
                    if time.time() > self._finish_time:
                        break
                    self._datetime = time
                    self._price = price
                    self._volume = volume
                    self._prices.append(price)
                    if not started and len(self._prices) >= self._intervals_after_start:
                        self._strategy.on_start(self)
                        started = True
                    if started:
                        self._on_tick()
                self._on_finish_day()
                self._prices.clear()

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

    # strategy.test()

    def get_datetime(self) -> datetime.datetime:
        return self._datetime

    def get_price(self) -> float:
        return self._price

    def get_prices(self) -> list[float]:
        return self._prices

    def get_volume(self) -> int:
        return self._volume

    def is_open_position(self) -> bool:
        return self._position is not None

    def get_position(self) -> Union[OpenPosition, None]:
        return self._position

    # general information

    def get_day_close_prices(self) -> list[float]:
        return self._day_close_prices

    def get_trades_history(self) -> list[list[Trade]]:
        return self._trades_history

    def get_days(self) -> list[datetime.datetime]:
        return self._days

    def get_ticker(self) -> str:
        return self._ticker

    def open_position(
        self,
        duration: Union[None, int] = None,
        keep_silent_duration=True,
        take_profit: Union[float, None] = None,
        stop_loss: Union[float, None] = None,
    ) -> OpenPosition:
        """
        Открывает позицию
        :param duration: длина позиции в числе периодов interval
        :param keep_silent_duration: не вызывать tick() до того, как позиция будет закрыта из-за истечения срока
        :param take_profit: take profit
        :param stop_loss: stop loss
        :return: открытую позицию OpenPosition
        """
        assert self._position is None
        self._position = OpenPosition(self._datetime, self._interval, self._price, duration, keep_silent_duration, take_profit, stop_loss)
        return self._position

    def close_position(self):
        assert self._position is not None
        self._trades_history[-1].append(self._position.close(self._datetime, self._price))
        self._position = None

    # utility functions

    def _on_finish_day(self):
        self._strategy.on_finish(self)
        if self.is_open_position():
            self.close_position()
        self._day_close_prices.append(self._price)

    def _on_tick(self):
        if self._position is not None:
            # take profit and stop loss
            if self._price >= self._position.take_profit or self._price <= self._position.stop_loss:
                self.close_position()
            # duration
            if self._position.expected_close is not None:
                if self._datetime >= self._position.expected_close:
                    self.close_position()
                elif self._position.keep_silent_duration:
                    return
        self._strategy.tick(self)
