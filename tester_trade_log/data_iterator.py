import datetime
import os
from typing import Union
from tester_trade_log.constants import EXCHANGE_OPEN


class DataIterator:
    def __init__(self, data_directory: str, ticker: str, period: datetime.timedelta):
        self._data_directory = data_directory
        self._ticker = ticker
        self._period: datetime.timedelta = period

        cache_directory = os.path.join(self._data_directory, "cache")
        cache_file_name = f"{self._ticker}.{self._period.total_seconds()}.txt"
        self._cache_full_path = os.path.join(cache_directory, cache_file_name)
        if cache_file_name not in os.listdir(cache_directory):
            data_full_path = os.path.join(self._data_directory, f"{self._ticker}.txt")
            self._make_cache(data_full_path, self._cache_full_path)

    def __iter__(self):
        return self._day_iterator()

    @staticmethod
    def _data_from_row(row: list[str]):
        # return [time, price, volume]
        return datetime.datetime.strptime(row[0], "%H%M%S"), float(row[1]), int(row[2])

    @staticmethod
    def _format_row(time: datetime.datetime, price: float, volume: int):
        return f"{time.strftime('%H%M%S')} {price} {volume}\n"

    def _make_cache(self, data_full_path: str, cache_full_path: str):
        with open(cache_full_path, "w") as cache_file:
            with open(data_full_path) as data_file:
                data = []
                row = data_file.readline().split()
                while True:
                    # day starts
                    # row contains date or is empty
                    if data:
                        # dump data
                        data[0] = f"{data[0]} {len(data) - 1}\n"
                        cache_file.writelines(data)
                    if len(row) == 0:
                        # end of file
                        return
                    # add date to data
                    data = [row[0]]
                    # read intraday time, price, volume
                    row = data_file.readline().split()
                    current_time, current_price, current_volume = self._data_from_row(row)
                    current_time = self._format_current_time(current_time)
                    row = data_file.readline().split()
                    while len(row) == 3:
                        time, price, volume = self._data_from_row(row)
                        while time - current_time >= self._period:
                            current_time += self._period
                            data.append(self._format_row(current_time, current_price, current_volume))
                            current_volume = 0
                        current_price = price
                        current_volume += volume
                        row = data_file.readline().split()
                    # write last volume
                    if current_volume:
                        data.append(self._format_row(current_time + self._period, current_price, current_volume))

    def _format_current_time(self, current_time: datetime.datetime):
        # делаем так, чтобы current_time был равен EXCHANGE_OPEN + k * _interval
        time_from_open = current_time - datetime.datetime.combine(current_time.date(), EXCHANGE_OPEN)
        return current_time - time_from_open % self._period

    def _day_iterator(self):
        # return [day, intraday_iterator]
        with open(self._cache_full_path) as cache_file:
            row = cache_file.readline().split()
            while row:
                day, n_observations = row
                day = datetime.datetime.strptime(day, "%Y%m%d").date()
                intraday_data = []
                row = cache_file.readline().split()
                while len(row) == 3:
                    intraday_data.append([datetime.datetime.combine(day, datetime.datetime.strptime(row[0], "%H%M%S").time()),
                                          float(row[1]),
                                          int(row[2])])
                    row = cache_file.readline().split()
                yield day, intraday_data
