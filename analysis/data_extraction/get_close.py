import os
import pandas as pd


def time_range_generator(start, finish, d_s):
    h, m, s = start
    while (h, m, s) <= finish:
        yield h * 10000 + m * 100 + s
        s += d_s
        if s >= 60:
            m += s // 60
            s %= 60
            if m >= 60:
                h += m // 60
                m = m % 60


# time: hh:mm:ss
delta_s = 60
start_time = (10, delta_s // 100, 0)
finish_time = (18, 40, 0)
time_range = list(time_range_generator(start_time, finish_time, delta_s))

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
