import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm


def get_data(directory: str, ticker: str, period: datetime.timedelta, horizon: int):
    data_pass = directory + ticker + "_" + str(period.total_seconds()) + "_" + str(horizon) + ".csv"
    return pd.read_csv(data_pass, sep="\t")


main_directory = "analysis/data/indicator_data/"
main_ticker = "AFKS"
main_period = datetime.timedelta(minutes=1)
main_horizon = 1
df = get_data(main_directory, main_ticker, main_period, main_horizon)
# print(sum(df['trand_of_price']) / df.shape[0])
df["change_of_price"] = df["new_price"] - df["close"]
df["old_change_of_price"] = df["change_of_price"].shift(-1)
df = df.dropna()
good_columns = [
    "close",
    "volume",
    "rsi",
    "tsi",
    "kama",
    "roc",
    "srsi",
    "ppo",
    "pvo",
    "aroon",
    "macd",
    "ema",
    "sma",
    "wma",
    "trix",
    "ksti",
    "dpoi",
    "stc",
    "blb",
    "ulc",
    "obv",
    "frc",
    "vpt",
    "npt",
    "new_price",
    "trand_of_price",
    "change_of_price",
    "old_change_of_price",
]
print(sm.stats.acorr_ljungbox(df["change_of_price"], lags=[10], return_df=True))

corr = df[["old_change_of_price", "change_of_price"]].corr()
fig, ax = plt.subplots(figsize=(10, 10))
sns.heatmap(corr, xticklabels=corr.columns.values, yticklabels=corr.columns.values, cmap="Blues", annot=True, label=main_ticker)
plt.show()
