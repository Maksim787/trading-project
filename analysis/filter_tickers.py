import os

os.chdir("data")
files = os.listdir("tickers")
print(files)
with open("dates.txt") as f:
    dates = f.readlines()
    n_dates = len(dates)
n_data = []
for i, file in enumerate(files, 1):
    print(f"{file} ({i}/{len(files)})")
    with open(f"tickers/{file}") as f:
        data = f.read()
    if len(data.split()) / 249 >= 560:
        print(f"take {file}")
        with open(f"relevant_tickers/{file}", "w") as f:
            f.write(data)
