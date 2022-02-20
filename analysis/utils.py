import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import math

from matplotlib.ticker import FuncFormatter


# read ticker.csv
# return (prices_by_day, time)
# prices_by_day[date] = day_price_list
# time = list of time in seconds
def read_ticker(ticker):
    df = pd.read_csv(f"../data/clean_tickers/{ticker}.csv")
    groups = df.groupby("DATE")
    prices_by_day = groups["PRICE"].apply(list).to_dict()
    time = list(groups["TIME"].get_group(next(iter(groups.groups.keys()))))
    assert list(map(int, time)) == sorted(map(int, time))
    return prices_by_day, convert_to_seconds(time)


def to_seconds(t):
    t = str(t)
    h = int(t[0:2])
    m = int(t[2:4])
    s = int(t[4:6])
    assert m <= 59 and s <= 59, f"{m = }, {s = }"
    return h * 60 * 60 + m * 60 + s


def convert_to_seconds(time):
    return [to_seconds(t) for t in time]


def format_time(t):
    t = int(t)
    h = t // 60 ** 2
    m = t // 60 % 60
    return f"{h}:{m:02d}"


def format_day(d):
    d = str(d)
    return f"{d[6:8]}.{d[4:6]}.{d[0:4]}"


def plot_with_time():
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x_val, tick_pos: format_time(x_val)))
    return fig, ax


# plot day prices
# x: time; y: day_prices
def plot_day_prices(prices_by_day, day, time, ticker=""):
    fig, ax = plot_with_time()
    ax.set_title(ticker + " " + format_day(day))
    ax.plot(time, prices_by_day[day])
    plt.show()


def log_returns(prices_by_day):
    return [[math.log(price_list[i + 1]) - math.log(price_list[i]) for i in range(len(price_list) - 1)] for price_list in prices_by_day.values()]


# return dataset_by_day = [day_1_dataset, day_2_dataset, ...]
# day_1_dataset = ([predictors_1_list, predictors_2_list, ...], [y_1, y_2, ...])
# len(predictors_1_list) = n_pred
def returns_window(returns, n_pred):
    day_return_len = len(returns[0])
    result = []
    for day_returns in returns:
        assert len(day_returns) == day_return_len, f"{len(day_returns) = }, {day_return_len = }"
        y = day_returns[n_pred:]
        predictors = [day_returns[i : i + n_pred] for i in range(len(day_returns) - n_pred)]
        result.append((predictors, y))
    return result


def add_time(dataset_by_day, time):
    for day_data in dataset_by_day:
        assert len(time) == len(day_data[0]), f"{len(time) = }, {len(day_data[0]) = }"
        for i, predictor_list in enumerate(day_data[0]):
            predictor_list.append(time[i])


# return dataset_by_day[:train_size], dataset_by_day[train_size:]
def train_test_split(dataset_by_day, ratio=0.7):
    train_size = int(round(len(dataset_by_day) * ratio))
    return dataset_by_day[:train_size], dataset_by_day[train_size:]


# get (X, y) from returns_window dataset
def get_X_y(dataset_by_day):
    X = sum((day_dataset[0] for day_dataset in dataset_by_day), [])
    y = sum((day_dataset[1] for day_dataset in dataset_by_day), [])
    return np.array(X), np.array(y).reshape(-1, 1)
