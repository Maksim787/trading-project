import os
import shutil
import zipfile
import time
import csv
from io import TextIOWrapper

os.chdir("../data")

all_files = os.listdir()

# make data/{dir_name} directory
dst_dir_name = "tickers_order_log"
if dst_dir_name in all_files:
    # shutil.rmtree(dst_dir_name)
    pass
if dst_dir_name in all_files:
    os.mkdir(dst_dir_name)

assert "zip" in all_files, "data/zip folder not found"
zip_files = ["zip/" + x for x in os.listdir("zip")]
dates = []
tickers = {}


def open_file(zip_ref):
    files = zip_ref.namelist()
    assert len(files) == 2
    trade_log = next(filter(lambda x: x.startswith("TradeLog"), files))  # trades
    order_log = next(filter(lambda x: x.startswith("OrderLog"), files))  # orders
    date = zip_file.removeprefix("zip/OrderLog").removesuffix(".zip")
    dates.append(date)
    # date = "%Y%m%d%H%M%S%f"
    date = 10 ** 9 * int(date)
    # open
    with zip_ref.open(order_log, "r") as f:
        reader = csv.reader(TextIOWrapper(f, "utf-8"))
        columns = next(reader)
        for row in reader:
            ticker = row[1]
            row[3] = str(int(row[3]) + date)
            writer = tickers.get(ticker)
            if writer is None:
                writer = csv.writer(open(f"{dst_dir_name}/{ticker}.csv", "w", newline=""))
                writer.writerow(columns)
                tickers[ticker] = writer
            writer.writerow(row)


print("Unzip")

start = time.time()
last = time.time()

for i, zip_file in enumerate(zip_files, 1):
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            open_file(zip_ref)
            print(f"Opened {i}/{len(zip_files)}, time: {time.time() - last:.1f}, total: {time.time() - start:.1f} s")
            last = time.time()
    except zipfile.BadZipFile:
        print(f"[ERROR] Не удалось считать {zip_file}")

# write dates
with open("dates.txt", "w") as f:
    print(*dates, sep="\n", file=f)
