import datetime
import os
from tester_trade_log.constants import EXCHANGE_OPEN


class PeriodData:
    def __init__(self, period: datetime.timedelta, time: datetime.datetime, price: float, volume: int):
        self.period = period
        self.time = self._format_period_time(time)
        self.close = price
        self.high = price
        self.low = price
        self.volume = volume

    def _format_period_time(self, current_time: datetime.datetime):
        # делаем так, чтобы current_time был равен EXCHANGE_OPEN + k * period
        time_from_open = current_time - datetime.datetime.combine(current_time.date(), EXCHANGE_OPEN)
        return current_time - time_from_open % self.period

    def add_data(self, time: datetime.datetime, price: float, volume: int):
        assert self.time <= time < self.time + self.period
        self.close = price
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.volume += volume

    def is_ready(self, time: datetime.datetime) -> bool:
        return time - self.time >= self.period

    def get_data(self) -> str:
        self.time += self.period
        row = f"{self.time.strftime('%H%M%S')} {self.close} {self.high} {self.low} {self.volume}\n"
        self.high = self.low = self.close
        self.volume = 0
        return row

    def format_row(self) -> str:
        return f"{self.time.strftime('%H%M%S')} {self.close} {self.high} {self.low} {self.volume}\n"


class DataIterator:
    def __init__(self, data_directory: str, ticker: str, period: datetime.timedelta):
        self._data_directory = data_directory
        self._ticker = ticker
        self._period: datetime.timedelta = period

        cache_directory = os.path.join(self._data_directory, "cache")
        if "cache" not in os.listdir(self._data_directory):
            os.mkdir(cache_directory)
        cache_file_name = f"{self._ticker}.{self._period.total_seconds()}.txt"
        self._cache_full_path = os.path.join(cache_directory, cache_file_name)
        if cache_file_name not in os.listdir(cache_directory):
            data_full_path = os.path.join(self._data_directory, f"{self._ticker}.txt")
            self._make_cache(data_full_path, self._cache_full_path)

    def __iter__(self):
        return self._day_iterator()

    @staticmethod
    def _data_from_row(row: list[str]) -> tuple[datetime.datetime, float, int]:
        # return (time, price, volume)
        return datetime.datetime.strptime(row[0], "%H%M%S"), float(row[1]), int(row[2])

    def _make_cache(self, data_full_path: str, cache_full_path: str):
        row_size = 3
        # row = [time, price, high, low, volume]
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
                    row = self._data_from_row(data_file.readline().split())
                    period_data = PeriodData(self._period, *row)
                    row = data_file.readline().split()
                    while len(row) == row_size:
                        row = self._data_from_row(row)
                        while period_data.is_ready(row[0]):
                            data.append(period_data.get_data())
                        period_data.add_data(*row)
                        row = data_file.readline().split()
                    # write last volume
                    if period_data.volume > 0:
                        data.append(period_data.get_data())

    def _day_iterator(self):
        # return [day, intraday_data]
        # intraday_data = list[time, price, high, low, volume]
        row_size = 5
        with open(self._cache_full_path) as cache_file:
            row = cache_file.readline().split()
            while row:
                day, n_observations = row
                day = datetime.datetime.strptime(day, "%Y%m%d").date()
                time = []
                close = []
                high = []
                low = []
                volume = []
                row = cache_file.readline().split()
                while len(row) == row_size:
                    time.append(datetime.datetime.combine(day, datetime.datetime.strptime(row[0], "%H%M%S").time()))
                    close.append(float(row[1]))
                    high.append(float(row[2]))
                    low.append(float(row[3]))
                    volume.append(int(row[4]))
                    row = cache_file.readline().split()
                yield day, (time, close, high, low, volume)
