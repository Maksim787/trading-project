import yfinance as yf
import os


class DataGetter:
    def __init__(self):
        self.cached = set(os.listdir("data/cache"))

    def get_stock(self, stock_name: str, start: str, end: str, interval: str) -> list[float]:
        cache_name = f"{stock_name}.{start}.{end}.{interval}.txt"
        if cache_name in self.cached:
            with open("data/cache/" + cache_name) as f:
                return list(map(float, f.readline().split()))
        result = list(yf.download(stock_name, start=start, end=end, interval=interval)['Adj Close'])
        with open("data/cache/" + cache_name, "w") as f:
            print(*result, file=f)
        return result


if __name__ == "__main__":
    getter = DataGetter()
    r = getter.get_stock('SBER.ME', start='2020-01-01', end='2021-01-01', interval='1d')
    print(r)
