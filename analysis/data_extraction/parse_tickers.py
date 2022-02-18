import os
import zipfile
import time
import pandas as pd

os.chdir("../data")

all_files = os.listdir()

# make data/tickers directory
if "tickers" not in all_files:
    os.mkdir("tickers")
assert "zip" in all_files, "data/zip folder not found"

zip_files = ["zip/" + x for x in os.listdir("zip")]
columns = ["DATE", "TIME", "PRICE", "VOLUME"]
tickers = {}  # tickers[name] = [(date, time, price, volume)]
dates = []


def open_file(zip_ref, tickers, dates):
    names = zip_ref.namelist()
    assert len(names) == 2
    trade_log = next(filter(lambda x: x.startswith("TradeLog"), names))  # trades
    order_log = next(filter(lambda x: x.startswith("OrderLog"), names))  # orders
    date = zip_file.removeprefix("zip/OrderLog").removesuffix(".zip")
    dates.append(date)
    # open
    df = pd.read_csv(zip_ref.open(trade_log), usecols=["SECCODE", "TIME", "PRICE", "VOLUME"])
    # assert (df["TIME"].values != df["TIME"].sort_values().values).sum() == 0
    for ticker, group in df.groupby("SECCODE"):
        if ticker not in tickers:
            create_ticker(ticker)
            tickers[ticker] = []
        tickers[ticker].extend(
            [(date, time, price, volume) for time, price, volume in zip(group["TIME"].tolist(), group["PRICE"].tolist(), group["VOLUME"].tolist())]
        )
    del df


def create_ticker(ticker):
    # create tickers/ticker.csv
    # write columns
    with open(f"tickers/{ticker}.csv", "w") as f:
        f.write(",".join(columns))
        f.write("\n")


def append_tickers():
    for ticker, data_list in tickers.items():
        if data_list:
            with open(f"tickers/{ticker}.csv", "a") as f:
                lines = [",".join(map(str, point)) for point in data_list]
                f.write("\n".join(lines))
                f.write("\n")
            tickers[ticker] = []


print("Unzip")

start = time.time()
last = time.time()

for i, zip_file in enumerate(zip_files, 1):
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            open_file(zip_ref, tickers, dates)
            append_tickers()
            print(f"Opened {i}/{len(zip_files)}, time: {time.time() - last:.1f}, total: {time.time() - start:.1f} s")
            last = time.time()
    except zipfile.BadZipFile:
        print(f"[ERROR] Не удалось считать {zip_file}")

# write dates
with open("dates.txt", "w") as f:
    print(*dates, sep="\n", file=f)
