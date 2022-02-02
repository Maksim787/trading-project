import testing.tester as tester_module


class BaseStrategy:
    name = ""

    def initialize(self, t: tester_module.Tester):
        """
        задает параметры стратегии: даты начала и конца, интервал, используемый список активов, начальное количество денег

        :return:
        """
        raise NotImplementedError

    def make_tick(self, t: tester_module.Tester):
        """
        делает покупки и продажи активов, создает позиции

        :return:
        """
        raise NotImplementedError
