from typing import List


def shrink(prices: List[float]):
    """
    сжимает повторы в один элемент
    :param prices:
    :return:
    """
    j = 1
    for i in range(1, len(prices)):
        if prices[i] != prices[i - 1]:
            prices[j] = prices[i]
            j += 1
    while len(prices) > j:
        prices.pop()


def count_n1_n2(prices):
    n1 = 0
    n2 = 0
    for i in range(1, len(prices)):
        if prices[i] - prices[i - 1] > 0:
            n1 += 1
        elif prices[i] - prices[i - 1] < 0:
            n2 += 1
        else:
            raise AssertionError
    assert n1 + n2 == len(prices) - 1
    return n1, n2


def count_runs(prices):
    cnt = 0
    prev_direction = prices[1] > prices[0]
    for i in range(2, len(prices)):
        direction = prices[i] > prices[i - 1]
        if direction != prev_direction:
            cnt += 1
            prev_direction = direction
    return cnt + 1
