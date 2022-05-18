import pandas as pd
import os

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


def print_table(function, table_names, table_file, caption, label, postfix):
    df1 = function(table_names[0])
    df2 = function(table_names[1])
    df1.columns = [column + postfix[0] for column in df1.columns]
    df2.columns = [column + postfix[1] for column in df2.columns]
    df = pd.concat((df1, df2), axis=1)
    with open(table_file, "w", encoding="utf-8") as f:
        print(df.to_latex(caption=caption, label=label), file=f)


print_table(
    get_trades_table,
    ["trades_crossing_train.csv", "trades_simple_train.csv"],
    "latex/rsi_simple_trades_train.tex",
    caption="Прибыль по сделкам стратегий (1) и (2) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_simple_trade",
    postfix=[" (1)", " (2)"],
)
print_table(
    get_days_table,
    ["days_crossing_train.csv", "days_simple_train.csv"],
    "latex/rsi_simple_days_train.tex",
    caption="Прибыль по дням стратегий (1) и (2) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_simple_day",
    postfix=[" (1)", " (2)"],
)

print_table(
    get_trades_table,
    ["trades_simple_test.csv", "trades_tree_0.csv"],
    "latex/rsi_tree_trades_test.tex",
    caption="Прибыль по сделкам стратегий (2) и (3) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_tree_trade",
    postfix=[" (2)", " (3)"],
)
print_table(
    get_days_table,
    ["days_simple_test.csv", "days_tree_0.csv"],
    "latex/rsi_tree_days_test.tex",
    caption="Прибыль по дням стратегий (2) и (3) в \\% и её стандартное отклонение в \\%",
    label="table:rsi_tree_day",
    postfix=[" (2)", " (3)"],
)
