import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
from itertools import product


class Direction(Enum):
    Up = 0
    Down = 1
    Stay = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def get_direction(prev_price, next_price):
    if next_price > prev_price:
        return Direction.Up
    if next_price < prev_price:
        return Direction.Down
    return Direction.Stay


def get_changes(price_list):
    changes = []
    for i in range(len(price_list) - 1):
        changes.append(get_direction(price_list[i], price_list[i + 1]))
    return changes


def empty_chain(k):
    chain = {}
    for p in product(tuple(Direction), repeat=k):
        chain[p] = {}
        for next_change in tuple(Direction):
            chain[p][next_change] = 0
    return chain


def create_chain(price_list, k=1):
    """

    :param price_list:
    :param k: количество предыдущих наблюдений
    :return: chain[prev_changes][next_change] = count
    """
    changes = get_changes(price_list)
    chain = empty_chain(k)
    n = len(changes)
    for i in range(n - k):
        prev_changes = tuple(changes[i : i + k])
        next_change = changes[i + k]
        chain[prev_changes][next_change] += 1
    return chain


def merge_chains(chains):
    k = len(next(iter(chains[0].keys())))
    total_chain = empty_chain(k)
    for chain in chains:
        for prev_changes, next_changes in chain.items():
            for next_change, count in next_changes.items():
                total_chain[prev_changes][next_change] += count
    return total_chain


def normalize_chain(chain):
    k = len(next(iter(chain.keys())))
    normalized_chain = empty_chain(k)
    for prev_changes, next_changes in chain.items():
        total_count = sum(next_changes.values())
        for next_change, count in next_changes.items():
            normalized_chain[prev_changes][next_change] = count / total_count
    return normalized_chain


def print_chain(chain):
    for prev_changes, next_changes in chain.items():
        print(f"{list(prev_changes)}:")
        for next_change, count in next_changes.items():
            print(f"\t{next_change}: {count}")


def plot_chain(chain, show_stay=True):
    up = np.array([next_changes[Direction.Up] for prev_changes, next_changes in chain.items()])
    down = np.array([next_changes[Direction.Down] for prev_changes, next_changes in chain.items()])
    if show_stay:
        stay = np.array([next_changes[Direction.Stay] for prev_changes, next_changes in chain.items()])
    else:
        stay = np.zeros(len(up))
        s = up + down
        up /= s
        down /= s
    labels = [str(prev_changes) for prev_changes in chain]
    plt.xlabel("probability")
    plt.barh(labels, down, color="red", label="down")
    if show_stay:
        plt.barh(labels, stay, color="blue", label="stay", left=down)
    plt.barh(labels, up, color="green", label="up", left=down + stay)
    plt.axvline(x=0.5, color="black")
    plt.legend()
    plt.show()
