import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from typing import Tuple, Dict, List


def read_ticker(ticker: str) -> Tuple[Dict[str, List[float]], List[int]]:
    """
    read ticker.csv
    :param ticker:
    :return: (prices_by_day, time)
    prices_by_day[day] = цены внутри дня
    time = время внутри дня, соответствует наблюдениям цен внутри дня
    """
    df = pd.read_csv(f"../data/clean_tickers/{ticker}.csv")
    groups = df.groupby("DATE")
    prices_by_day = groups["PRICE"].apply(list).to_dict()
    time = list(groups["TIME"].get_group(next(iter(groups.groups.keys()))))
    assert list(map(int, time)) == sorted(map(int, time))
    return prices_by_day, list_to_seconds(time)


def to_seconds(t: int) -> int:
    """

    :param t: hh.mm.ss = 173100
    :return: time in seconds
    """
    t = str(t)
    assert len(t) == 6
    h = int(t[0:2])
    m = int(t[2:4])
    s = int(t[4:6])
    assert 0 <= m <= 59 and 0 <= s <= 59, f"{m = }, {s = }"
    return h * 60 * 60 + m * 60 + s


def list_to_seconds(time: List[int]):
    return [to_seconds(t) for t in time]


def format_time(t: int):
    t = int(t)
    h = t // 60 ** 2
    m = t // 60 % 60
    return f"{h}:{m:02d}"


def format_day(d: int) -> str:
    """
    :param d: yyyy.mm.d = 20150417
    :return:
    """
    d = str(d)
    return f"{d[6:8]}.{d[4:6]}.{d[0:4]}"


def get_at(index: float, time: List[int]) -> int:
    index = int(round(index))
    if index >= len(time):
        return time[-1]
    if index < 0:
        return time[0]
    return time[index]


def plot_with_time(time):
    """
    format time for x-axis
    :param time:
    :return:
    """
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x_val, tick_pos: format_time(get_at(x_val, time))))
    return fig, ax


def plot_with_days(days):
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x_val, tick_pos: format_day(get_at(x_val, days))))
    return fig, ax


def plot_day_prices(prices_by_day, day, time, ticker=""):
    """
    plot day prices
    x: time; y: day_prices
    :param prices_by_day:
    :param day:
    :param time:
    :param ticker:
    :return:
    """
    plot_with_time(time)
    plt.title(ticker + " " + format_day(day))
    plt.plot(prices_by_day[day])
    plt.show()
