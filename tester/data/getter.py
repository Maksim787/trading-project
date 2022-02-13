import yfinance as yf
import os
import datetime


class DataGetter:
    def __init__(self):
        self.cached = set(os.listdir("data/cache"))

    def get_equity(self, equity: str, start: datetime.date, end: datetime.date, interval: str) -> list[float]:
        """
        :param equity: название инструмента на finance.yahoo.com
        :param start: начало периода
        :param end: конец периода
        :param interval: интервал между наблюдениями: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        :return: список цен
        """

        start = start.isoformat()
        end = end.isoformat()
        cache_name = f"{equity}.{start}.{end}.{interval}.txt"
        if cache_name in self.cached:
            with open("data/cache/" + cache_name) as f:
                return list(map(float, f.readline().split()))
        result = list(yf.download(equity, start=start, end=end, interval=interval)["Adj Close"])
        with open("data/cache/" + cache_name, "w") as f:
            print(*result, file=f)
        return result


if __name__ == "__main__":
    getter = DataGetter()
    r = getter.get_equity("SBER.ME", start=datetime.date(2020, 1, 1), end=datetime.date(2021, 1, 1), interval="1d")
    print(r)
