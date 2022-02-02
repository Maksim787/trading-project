import datetime

from data.getter import DataGetter
from testing.tester import Tester
from result.capital import CapitalResult
from strategy.random_strategy import RandomStrategy
from strategy.bollinger_bands import BollingerBands

strategy = RandomStrategy
equity = "TCSG.ME"
data_getter = DataGetter()

dates = []
for i in range(7):
    date = datetime.date.today() - datetime.timedelta(days=i + 1)
    if date.weekday() <= 4:
        dates.append(date)
dates.reverse()
print(dates)
for date in dates:
    result = CapitalResult()
    tester = Tester(data_getter, [result])
    tester.test(strategy(equity, 1e7, date))
    result.plot_capital()
