import os
import pandas as pd

# time: hh:mm:ss
start_time = 100000
finish_time = 184000
delta = 100
time_range = list(range(start_time + delta, finish_time + 1, delta))

os.chdir("../data")


def flush_date(date, date_deals, info):
    # date_deals is not empty
    i = 0
    last_price = date_deals[0][1]  # first period prices are equal to second period prices if missed
    for time in time_range:
        total_volume = 0
        price = -1
        while i < len(date_deals):
            t, p, v = date_deals[i]
            if t > time:
                break
            total_volume += v
            price = p
            i += 1
        if price == -1:
            price = last_price
        info.append((date, time, price, total_volume))
        last_price = price


# minute interval:
# hh:mm:00
def get_close(data):
    info = []  # (date, time, price, volume)
    date_deals = []  # (time, price, volume)
    last_date = data["DATE"][0]
    for d, t, p, v in zip(data["DATE"], data["TIME"], data["PRICE"], data["VOLUME"]):
        if d != last_date:
            flush_date(last_date, date_deals, info)
            date_deals.clear()
            last_date = d
        date_deals.append((t, p, v))
    return info


files = os.listdir("relevant_tickers")
# make data/clean_tickers directory
if "clean_tickers" not in os.listdir():
    os.mkdir("clean_tickers")

for i, file in enumerate(files, 1):
    print(f"{file} ({i}/{len(files)})")
    data = pd.read_csv(f"relevant_tickers/{file}").to_dict("list")
    df = pd.DataFrame(get_close(data), columns=["DATE", "TIME", "PRICE", "VOLUME"])
    df.to_csv(f"clean_tickers/{file}", index=False)
