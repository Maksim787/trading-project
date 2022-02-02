import datetime

from data.getter import DataGetter
from testing.tester import Tester
from evaluate.result import TestResult
from strategy.random_strategy import RandomStrategy
from strategy.bollinger_bands import BollingerBands

strategy = BollingerBands
equity = "TCSG.ME"

dates = []
for i in range(7):
    date = datetime.date.today() - datetime.timedelta(days=i + 1)
    if date.weekday() <= 4:
        dates.append(date)
dates.reverse()
print(dates)
for date in dates:
    tester = Tester(DataGetter(), TestResult())
    result = tester.test(strategy(equity, 1e7, date))
    result.plot_capital()
