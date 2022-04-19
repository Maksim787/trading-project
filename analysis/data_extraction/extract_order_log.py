from analysis.data_extraction.data_extractor import DataExtractor
from typing import Union


def format_date(time, date):
    # date = "%Y%m%d%H%M%S%f"
    if len(time) == 12:
        return date * (10 ** 12) + time
    elif len(time) == 9:
        return date * (10 ** 9) + time
    else:
        raise AssertionError


with open("allowed_tickers.txt") as f:
    allowed_tickers = f.read().split()


def format_row(row: list[str], date: int) -> Union[tuple[str, str], None]:
    # row = [NO, SECCODE, BUYSELL, TIME, ORDERNO, ACTION, PRICE, VOLUME, TRADENO, TRADEPRICE]
    # return (time, price, volume_change, direction: 0-buy, 1-sell)
    if row[1] not in allowed_tickers or row[5] == "2":
        return None
    time = int(row[3])
    if len(row[3]) == 9:
        time += date * 10 ** 9
        time *= 10 ** 3
    elif len(row[3]) == 12:
        time += date * 10 ** 12
    else:
        raise AssertionError
    volume = row[7]
    if row[5] == "0":
        volume = "-" + volume
    if row[2] == "B":
        direction = "0"
    elif row[2] == "S":
        direction = "1"
    else:
        raise AssertionError
    return " ".join([str(time), row[6], volume, direction, "\n"]), row[1]


extractor = DataExtractor("../data/zip", "../data/tickers_order_log", format_row, ["OrderLog20150302.zip", "OrderLog20150522.zip"])
extractor.extract_orderlog()
