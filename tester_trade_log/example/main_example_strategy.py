from tester_trade_log.tester import Tester
from tester_trade_log.example.example_strategy import ExampleStrategy
from tester_trade_log.stats import print_stats


def main():
    tester = Tester("analysis/data/tickers_trade_log", ExampleStrategy("AFKS", days=10))
    tester.test()
    print_stats(tester)


if __name__ == "__main__":
    main()
