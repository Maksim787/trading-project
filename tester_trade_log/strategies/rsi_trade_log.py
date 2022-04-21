from tester_trade_log.strategies.rsi import RSIStrategy
from tester_trade_log.tester import Tester
from tester_trade_log.stats import print_stats

import os
from tqdm import tqdm


def get_tickers():
    tickers_files = os.listdir("analysis/data/tickers_trade_log")
    return [file.removesuffix(".txt") for file in tickers_files]


tickers = get_tickers()
sharpe_ratios = {}
tickers_tqdm = tqdm(tickers)
for ticker in tickers_tqdm:
    tickers_tqdm.set_description(ticker)
    strategy = RSIStrategy(ticker, 14, 0, 125)
    tester = Tester("analysis/data/tickers_trade_log", strategy)
    tester.test(show_progress=False)
    sharpe_ratios[ticker] = print_stats(tester)
for i, (ticker, (fig, (mean, std, ratio))) in enumerate(sorted(sharpe_ratios.items(), key=lambda kv: -kv[1][1][2])):
    print(f"{ticker}:\t{mean:.3f}% ± {std:.3f}%\t Sharpe Ratio = {ratio:.3f}")
    if i <= 9:
        fig.savefig(f"tester_trade_log/figures/{ticker}.png")
