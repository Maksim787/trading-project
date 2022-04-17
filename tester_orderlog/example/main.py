from tester_orderlog.tester import Tester
from tester_orderlog.example.example_strategy import ExampleStrategy

tester = Tester("../../analysis/data/tickers_order_log", ExampleStrategy("ASSB"))
tester.test()
