from data.getter import DataGetter
from testing.tester import Tester
from evaluate.result import TestResult
from strategy.random_strategy import RandomStrategy

tester = Tester(DataGetter(), TestResult())
result = tester.test(RandomStrategy("SBER.ME", 1e7))
result.plot_capital()
