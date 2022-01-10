import testing.tester as tester_module


class BaseStrategy:
    name = ""

    def initialize(self, t: tester_module.Tester):
        """
        Задает параметры стратегии

        :return:
        """
        raise NotImplementedError

    def make_tick(self, t: tester_module.Tester):
        """
        Принимает решение о создании новых ордеров

        :return:
        """
        raise NotImplementedError


if __name__ == "__main__":
    s = BaseStrategy()
