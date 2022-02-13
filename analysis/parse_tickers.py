import os
import zipfile
import pandas as pd

os.chdir("data")

all_files = sorted(os.listdir())

if "tickers" not in all_files:
    os.mkdir("tickers")

zip_files = ["zip/" + x for x in os.listdir("zip")]
tickers = {}  # tickers[ticker_str] = [(date, time, price, volume)]
dates = []


def open_file(zip_ref):
    names = zip_ref.namelist()
    assert len(names) == 2
    trade_log = next(filter(lambda x: x.startswith("TradeLog"), names))
    order_log = next(filter(lambda x: x.startswith("OrderLog"), names))
    date = zip_file.removeprefix("zip/OrderLog").removesuffix(".zip")
    dates.append(date)
    # open
    df = pd.read_csv(zip_ref.open(trade_log))
    df = df[["SECCODE", "TIME", "PRICE", "VOLUME"]]
    assert (df["TIME"].values != df["TIME"].sort_values().values).sum() == 0
    for ticker, group in df.groupby("SECCODE"):
        group = group.drop(columns=["SECCODE"])
        if ticker not in tickers:
            tickers[ticker] = []
        new_data = [(date, int(time), float(price), int(volume)) for time, price, volume in
                    zip(group["TIME"].values, group["PRICE"], group["VOLUME"])]
        tickers[ticker].extend(new_data)
    del df


def append_tickers(ind):
    for ticker, data_list in tickers.items():
        if ind == 0 or data_list:
            mode = "a" if ind != 0 else "w"
            with open(f"tickers/{ticker}.csv", mode) as f:
                lines = [",".join(map(str, point)) for point in data_list]
                f.write("\n".join(lines))
                f.write("\n")
            tickers[ticker] = []


print("Unzip")

for i, zip_file in enumerate(zip_files):
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            print(f"{i + 1}/{len(zip_files)}")
            open_file(zip_ref)
            append_tickers(i)
    except zipfile.BadZipFile:
        print(f"[ERROR] Не удалось считать {zip_file}")

with open("dates.txt", "w") as f:
    print(*dates, sep="\n", file=f)
