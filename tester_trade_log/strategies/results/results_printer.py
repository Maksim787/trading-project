import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

results_folder = "tester_trade_log/strategies/results"
os.chdir(results_folder)


def get_trades_table(name):
    df = pd.read_csv(name).replace("%", "", regex=True)
    df = df.drop(columns=["profitability", "profitability long", "profitability short"])
    df.columns = ["Тикер", "Прибыль", "Long", "Short"]
    df.set_index("Тикер", inplace=True)
    return df


def get_days_table(name):
    df = pd.read_csv(name).replace("%", "", regex=True)
    df = df.drop(
        columns=[
            "trades count",
            "long count",
            "short count",
            "profitability",
            "profitability long",
            "profitability short",
            "returns long",
            "returns short",
        ]
    )
    df.columns = ["Тикер", "Коэффициент Шарпа", "Прибыль в день"]
    df.set_index("Тикер", inplace=True)
    return df


def get_table(function, table_names, postfix):
    df1 = function(table_names[0])
    df2 = function(table_names[1])
    df1.columns = [column + postfix[0] for column in df1.columns]
    df2.columns = [column + postfix[1] for column in df2.columns]
    df = pd.concat((df1, df2), axis=1)
    return df


def print_table(function, table_names, postfix, table_file, caption, label):
    df = get_table(function, table_names, postfix)
    with open(table_file, "w", encoding="utf-8") as f:
        print(df.to_latex(caption=caption, label=label), file=f)


def extract_mean_std(column):
    return column.apply(lambda x: float(x[: x.find(" ")])), column.apply(lambda x: float(x[x.rfind(" ") :]))


def plot_returns(is_trade_plot, table_names, postfix, plot_file):
    if is_trade_plot:
        function = get_trades_table
        label = "Прибыль"
        title = "Средняя прибыль за сделку и её стандартное отклонение"
    else:
        label = "Прибыль в день"
        title = "Средняя прибыль за день и её стандартное отклонение"
        function = get_days_table
    df = get_table(function, table_names, postfix)
    df = df.drop(index=["TAER"])
    df = df.sort_values(by=label + postfix[0], key=lambda x: -extract_mean_std(x)[0])
    returns_1, std_1 = extract_mean_std(df[label + postfix[0]])
    returns_2, std_2 = extract_mean_std(df[label + postfix[1]])
    n_tickers = df.shape[0]
    x = np.linspace(1, n_tickers, n_tickers)
    plt.errorbar(x, returns_1, std_1, label="Стратегия" + postfix[0], fmt="o", capsize=3, alpha=0.7, color="C0")
    plt.errorbar(x + 0.5, returns_2, std_1, label="Стратегия" + postfix[1], fmt="o", capsize=3, alpha=0.7, color="C1")
    plt.axhline(0, color="black", alpha=0.3)
    plt.xlabel("Номер тикера")
    plt.ylabel("Прибыль в %")
    plt.title(title)
    plt.legend(loc="upper right")
    plt.savefig(os.path.join("figures", plot_file))
    plt.show()


plot_returns(True, ["trades_crossing_train.csv", "trades_simple_train.csv"], [" (1)", " (2)"], "1_2_trades.png")

plot_returns(True, ["trades_simple_test.csv", "trades_tree_0.csv"], [" (2)", " (3)"], "2_3_trades.png")

plot_returns(False, ["days_crossing_train.csv", "days_simple_train.csv"], [" (1)", " (2)"], "1_2_days.png")

plot_returns(False, ["days_simple_test.csv", "days_tree_0.csv"], [" (2)", " (3)"], "2_3_days.png")

print_table(
    get_trades_table,
    ["trades_crossing_train.csv", "trades_simple_train.csv"],
    [" (1)", " (2)"],
    "latex/rsi_simple_trades_train.tex",
    caption="Прибыль по сделкам стратегий (1) и (2) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_simple_trade",
)
print_table(
    get_days_table,
    ["days_crossing_train.csv", "days_simple_train.csv"],
    [" (1)", " (2)"],
    "latex/rsi_simple_days_train.tex",
    caption="Прибыль по дням стратегий (1) и (2) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_simple_day",
)

print_table(
    get_trades_table,
    ["trades_simple_test.csv", "trades_tree_0.csv"],
    [" (2)", " (3)"],
    "latex/rsi_tree_trades_test.tex",
    caption="Прибыль по сделкам стратегий (2) и (3) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_tree_trade",
)
print_table(
    get_days_table,
    ["days_simple_test.csv", "days_tree_0.csv"],
    [" (2)", " (3)"],
    "latex/rsi_tree_days_test.tex",
    caption="Прибыль по дням стратегий (2) и (3) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_tree_day",
)
