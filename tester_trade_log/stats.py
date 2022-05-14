from tester_trade_log.tester import Tester, Trade, DIRECTION

import os
import datetime
from tqdm import tqdm
import numpy as np
import pandas as pd

from typing import Callable
from prettytable import PrettyTable


class StrategyTester:
    def __init__(self, strategy_getter: Callable, data_directory, tickers=None):
        self._strategy_getter = strategy_getter
        self._data_directory = data_directory
        self._tickers = self._get_tickers() if tickers is None else tickers
        self._results_by_ticker: dict[str, Tester] = {}
        self._days: list[datetime.datetime] = []
        self._prices: list[datetime.datetime] = []

    def _get_tickers(self):
        tickers_files = os.listdir(self._data_directory)
        return [file.removesuffix(".txt") for file in tickers_files if file != "cache"]

    def get_tickers(self):
        return self._tickers

    def test(self):
        tickers_iterator = tqdm(self._tickers)
        for ticker in tickers_iterator:
            tickers_iterator.set_description(ticker)
            tester = Tester(self._data_directory, self._strategy_getter(ticker=ticker), ticker=ticker)
            tester.test()
            if not self._days:
                self._days = tester.get_days_history()
                self._prices = tester.get_day_close_price_history()
            tester.clear()
            self._results_by_ticker[ticker] = tester

    @staticmethod
    def _get_returns_by_day(trades: list[list[Trade]]) -> np.array:
        returns_by_day = []
        for today_trades in trades:
            returns = [trade.profit_ratio() for trade in today_trades]
            returns_by_day.append(np.product(returns))
        return np.array(returns_by_day) * 100 - 100

    @staticmethod
    def _get_trades_count_by_day(trades: list[list[Trade]]) -> np.array:
        return np.array([len(today_trades) for today_trades in trades])

    @staticmethod
    def _get_trade_type(trades: list[list[Trade]], direction: DIRECTION) -> list[list[Trade]]:
        direction_trades = []
        for trade_list in trades:
            direction_trades.append([trade for trade in trade_list if trade.direction == direction])
        return direction_trades

    @staticmethod
    def _get_trades_returns(trades: list[list[Trade]]) -> np.array:
        return np.array([trade.profit_ratio() * 100 - 100 for day_trades in trades for trade in day_trades])

    @staticmethod
    def profit_ratio(returns):
        return (returns > 0).sum() / len(returns) * 100

    def get_stats(self):
        records = []
        for ticker in self._tickers:
            tester = self._results_by_ticker[ticker]

            trades = tester.get_trades_history()
            long_trades = self._get_trade_type(trades, DIRECTION.LONG)
            short_trades = self._get_trade_type(trades, DIRECTION.SHORT)

            # total info
            trades_cnt = self._get_trades_count_by_day(trades)
            long_trades_cnt = self._get_trades_count_by_day(long_trades)
            short_trades_cnt = self._get_trades_count_by_day(short_trades)

            returns = self._get_trades_returns(trades)
            returns_long = self._get_trades_returns(long_trades)
            returns_short = self._get_trades_returns(short_trades)

            # day info
            returns_by_day = self._get_returns_by_day(trades)
            returns_by_day_long = self._get_returns_by_day(long_trades)
            returns_by_day_short = self._get_returns_by_day(short_trades)

            record = {
                "mean": returns.mean(),
                "std": returns.std(),
                "sharpe": returns.mean() / returns.std(),
                "mean long": returns_long.mean(),
                "std long": returns_long.std(),
                "mean short": returns_short.mean(),
                "std short": returns_short.std(),
                "count mean": trades_cnt.mean(),
                "count std": trades_cnt.std(),
                "long count mean": long_trades_cnt.mean(),
                "long count std": long_trades_cnt.std(),
                "short count mean": short_trades_cnt.mean(),
                "short count std": short_trades_cnt.std(),
                "profitability": self.profit_ratio(returns),
                "profitability long": self.profit_ratio(returns_long),
                "profitability short": self.profit_ratio(returns_short),
                "sharpe (days)": returns_by_day.mean() / returns_by_day.std(),
                "mean (days)": returns_by_day.mean(),
                "std (days)": returns_by_day.std(),
                "mean long (days)": returns_by_day_long.mean(),
                "std long (days)": returns_by_day_long.std(),
                "mean short (days)": returns_by_day_short.mean(),
                "std short (days)": returns_by_day_short.std(),
                "profitability (days)": self.profit_ratio(returns_by_day),
                "profitability long (days)": self.profit_ratio(returns_by_day_long),
                "profitability short (days)": self.profit_ratio(returns_by_day_short),
            }
            records.append(record)
        df = pd.DataFrame.from_records(records, index=self._tickers)
        return df

    @staticmethod
    def _format_mean_std(mean, std, precision, units=""):
        return f"{mean:.{precision}f}{units} ± {std:.{precision}f}{units}"

    @staticmethod
    def _format_value(value, precision, units=""):
        return f"{value:.{precision}f}{units}"

    def print_stats(self):
        df = self.get_stats()
        trades_info = PrettyTable(
            ["ticker", "returns", "profitability", "returns long", "profitability long", "returns short", "profitability short"], title="Trades info"
        )
        day_info = PrettyTable(
            [
                "ticker",
                "sharpe",
                "trades count",
                "long count",
                "short count",
                "returns",
                "profitability",
                "returns long",
                "profitability long",
                "returns short",
                "profitability short",
            ],
            title="Days info",
        )
        for ticker, row in sorted(df.iterrows(), key=lambda x: -x[1]["sharpe"]):
            trades_info.add_row(
                [
                    ticker,
                    self._format_mean_std(row["mean"], row["std"], 2, "%"),
                    self._format_value(row["profitability"], 1, "%"),
                    self._format_mean_std(row["mean long"], row["std long"], 2, "%"),
                    self._format_value(row["profitability long"], 1, "%"),
                    self._format_mean_std(row["mean short"], row["std short"], 2, "%"),
                    self._format_value(row["profitability short"], 1, "%"),
                ]
            )
            day_info.add_row(
                [
                    ticker,
                    self._format_value(row["sharpe"], 2),
                    self._format_mean_std(row["count mean"], row["count std"], 1),
                    self._format_mean_std(row["long count mean"], row["long count std"], 1),
                    self._format_mean_std(row["short count mean"], row["short count std"], 1),
                    self._format_mean_std(row["mean (days)"], row["std (days)"], 2, "%"),
                    self._format_value(row["profitability (days)"], 1, "%"),
                    self._format_mean_std(row["mean long (days)"], row["std long (days)"], 2, "%"),
                    self._format_value(row["profitability long (days)"], 1, "%"),
                    self._format_mean_std(row["mean short (days)"], row["std short (days)"], 2, "%"),
                    self._format_value(row["profitability short (days)"], 1, "%"),
                ]
            )
        print(trades_info)
        print(day_info)
