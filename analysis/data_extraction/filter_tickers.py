import os

daily_lower_bound = 560

os.chdir("../data")

with open("dates.txt") as f:
    n_days = len(f.readlines())

tickers = os.listdir("tickers")
# make data/relevant_tickers directory
if "relevant_tickers" not in os.listdir():
    os.mkdir("relevant_tickers")
n_data = []
for i, file in enumerate(tickers, 1):
    print(f"{file} parsing ({i}/{len(tickers)})")
    with open(f"tickers/{file}") as f:
        data = f.read()
    n_daily_deals = (len(data.split()) - 1) / n_days
    if n_daily_deals >= daily_lower_bound:
        print(f"{file} taken ({n_daily_deals} daily deals)")
        with open(f"relevant_tickers/{file}", "w") as f:
            f.write(data)
