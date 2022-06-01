from tester_trade_log.tester import Trade

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

results_folder = "tester_trade_log/strategies/results/data"
os.chdir(results_folder)


def load_trades(strategy_name) -> dict[str, list[list[Trade]]]:
    directory = f"detailed_results_{strategy_name}"
    tickers = os.listdir(directory)
    trades_dict = {}
    for ticker in tickers:
        if ticker != "TAER.pickle":
            with open(os.path.join(f"detailed_results_{strategy_name}", ticker), "rb") as f:
                trades_dict[ticker.removesuffix(".pickle")] = pickle.load(f)
    return trades_dict


def profit_ratio(trade: Trade, commission: float):
    return (
        1
        + ((trade.close_price - trade.open_price) * trade.direction.value - commission / 100 * (trade.open_price + trade.close_price))
        / trade.open_price
    )


def get_returns_by_day(trades: list[list[Trade]], commission: float) -> np.ndarray:
    returns_by_day = []
    for today_trades in trades:
        returns = [profit_ratio(trade, commission) for trade in today_trades]
        returns_by_day.append(np.product(returns))
    return np.array(returns_by_day) * 100 - 100


def plot_commission_line(ticker, trades, min_commission=0, max_commission=0.3, n=50):
    commissions = np.linspace(min_commission, max_commission, n)
    returns = []
    for commission in commissions:
        returns.append(get_returns_by_day(trades, commission).mean())
    plt.plot(commissions, returns)
    plt.axhline(0)
    plt.title(ticker)
    plt.show()


def on_ticker_trades(trades: list[list[Trade]], commission: float):
    returns_by_day = get_returns_by_day(trades, commission)
    mean = returns_by_day.mean()
    std = returns_by_day.std()
    return mean, std


def get_mean_std(name, commissions):
    trades_by_ticker = load_trades(name)
    mean_std_by_commission = {}
    for commission in commissions:
        means = []
        stds = []
        tickers = sorted(trades_by_ticker.keys(), key=lambda ticker: -get_returns_by_day(trades_by_ticker[ticker], commission).mean())
        for ticker in tickers:
            trades = trades_by_ticker[ticker]
            # plot_commission_line(ticker, trades)
            returns_by_day = get_returns_by_day(trades, commission)
            means.append(returns_by_day.mean())
            stds.append(returns_by_day.std())
        mean_std_by_commission[commission] = (means, stds)
    return mean_std_by_commission


def plot_strategy(name, commissions, plot_file=""):
    mean_std_by_commission = get_mean_std(name, commissions)

    for commission in commissions:
        means, stds = mean_std_by_commission[commission]
        x = np.linspace(1, len(means), len(means))
        plt.errorbar(x, means, stds, fmt="o", capsize=3, alpha=0.7, color="C0")
        plt.xlabel("Номер тикера")
        plt.ylabel("Прибыль в %")
        plt.title(f"Комиссия {commission}%")
        plt.axhline(0, color="black", alpha=0.3)
        if plot_file:
            plt.savefig(os.path.join("figures", plot_file))
        plt.show()


def plot_strategies(*args, commissions=None, plot_file=""):
    if commissions is None:
        commissions = [0]
    model_names = args
    mean_std_by_commission = [get_mean_std(name, commissions) for name in model_names]
    n = len(model_names)
    for commission in commissions:
        for i, model_name in enumerate(model_names):
            mean, std = mean_std_by_commission[i][commission]
            x = np.linspace(1, len(mean), len(mean))
            plt.errorbar(x + i / n, mean, std, label="Стратегия " + model_name, fmt="o", capsize=3, alpha=0.7, color=f"C{i}")
        plt.title(f"Сравнение стратегий при комиссии {commission}%")
        plt.xlabel("Номер тикера")
        plt.ylabel("Прибыль в %")
        plt.legend(loc="upper right")
        plt.axhline(0, color="black", alpha=0.3)
        if plot_file:
            plt.savefig(os.path.join("figures", plot_file))
        plt.show()


def main():
    commissions = [0, 0.01, 0.02, 0.025, 0.05, 0.06, 0.3]
    plot_strategy("tree_0", commissions)
    plot_strategies("tree_0", "tree_0.01", "tree_0.02", "tree_0.05")
    plot_strategies("forest_0", "forest_0.01", "forest_0.02", "forest_0.05")
    plot_strategies("tree_0", "forest_0")


if __name__ == "__main__":
    main()
