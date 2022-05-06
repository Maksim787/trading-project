import datetime
import os
from typing import Union
from tester_trade_log.constants import EXCHANGE_OPEN


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
