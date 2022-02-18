import os

daily_lower_bound = 560
with open("data/dates.txt") as f:
    n_days = len(f.readlines())

os.chdir("data")
files = os.listdir("tickers")
if "relevant_tickers" not in os.listdir():
    os.mkdir("relevant_tickers")
with open("dates.txt") as f:
    dates = f.readlines()
    n_dates = len(dates)
n_data = []
for i, file in enumerate(files, 1):
    print(f"{file} ({i}/{len(files)})")
    with open(f"tickers/{file}") as f:
        data = f.read()
    if (len(data.split()) - 1) / n_days >= daily_lower_bound:
        print(f"take {file}")
        with open(f"relevant_tickers/{file}", "w") as f:
            f.write(data)
