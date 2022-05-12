import numpy as np
import math


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
