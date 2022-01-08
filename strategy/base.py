from typing import *

import testing.tester as t


class BaseStrategy:
    name = ""

    def __init__(self):
        self.tester: Union[t.Tester, None] = None

    def initialize(self):
        """
        Задает параметры стратегии

        :return:
        """
        raise NotImplementedError

    def make_tick(self):
        """
        Принимает решение о создании новых ордеров

        :return:
        """
        raise NotImplementedError


if __name__ == "__main__":
    s = BaseStrategy()
