from tester_trade_log.tester import Tester, Trade, DIRECTION

import os
import datetime
from tqdm import tqdm
import numpy as np
import pandas as pd

from typing import Callable


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
    def _get_trade_type(trades: list[list[Trade]], direction: DIRECTION):
        direction_trades = []
        for trade_list in trades:
            direction_trades.append([trade for trade in trade_list if trade.direction == direction])
        return direction_trades

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

            long_trades_cnt = np.array([len(today_trades) for today_trades in long_trades]).mean()
            short_trades_cnt = np.array([len(today_trades) for today_trades in short_trades]).mean()

            returns_by_day = self._get_returns_by_day(trades)
            returns_by_day_long = self._get_returns_by_day(long_trades)
            returns_by_day_short = self._get_returns_by_day(short_trades)

            total_profitable = self.profit_ratio(returns_by_day)
            long_profitable = self.profit_ratio(returns_by_day_long)
            short_profitable = self.profit_ratio(returns_by_day_short)

            mean, std = returns_by_day.mean(), returns_by_day.std()
            record = {
                "mean": mean,
                "std": std,
                "sharpe": mean / std,
                "total trades": long_trades_cnt + short_trades_cnt,
                "total profitability": total_profitable,
                "long trades": long_trades_cnt,
                "short trades": short_trades_cnt,
                "long/short ratio": long_trades_cnt / short_trades_cnt,
                "long mean": returns_by_day_long.mean(),
                "long std": returns_by_day_long.std(),
                "long profitability": long_profitable,
                "short mean": returns_by_day_short.mean(),
                "short std": returns_by_day_short.std(),
                "short profitability": short_profitable,
            }
            records.append(record)
        df = pd.DataFrame.from_records(records, index=self._tickers)
        return df

    def print_stats(self):
        df = self.get_stats()
        for ticker, row in sorted(df.iterrows(), key=lambda x: -x[1]["sharpe"]):
            print(
                f"{ticker}:\t"
                f"sharpe: {row['sharpe']:.2f}\t"
                f"total: {row['mean']:.2f} ± {row['std']:.2f} ({row['total trades']:4.1f} trades), {row['total profitability']:.1f}% profitable\t"
                f"long: {row['long mean']:.2f} ± {row['long std']:.2f} ({row['long trades'] / row['total trades'] * 100:.1f}%), {row['long profitability']:.1f}% profitable\t"
                f"short: {row['short mean']:.2f} ± {row['short std']:.2f} ({row['short trades'] / row['total trades'] * 100:.1f}%), {row['short profitability']:.1f}% profitable"
            )
