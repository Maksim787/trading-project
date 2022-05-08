from analysis.data_extraction.data_extractor import DataExtractor
from typing import Union

with open("analysis/data_extraction/allowed_tickers.txt") as f:
    allowed_tickers = f.read().split()

last_date_by_ticker = {}


def format_row(row: list[str], date: int) -> Union[tuple[str, str], None]:
    # row = [TRADENO, SECCODE, TIME, BUYORDERNO, SELLORDERNO, PRICE, VOLUME]
    ticker = row[1]
    if ticker not in allowed_tickers:
        return None
    assert len(row[2]) == 6

    prefix = ""
    last_date = last_date_by_ticker.get(ticker, 20000101)
    if last_date != date:
        prefix = f"{date}\n"
        last_date_by_ticker[ticker] = date

    return f"{prefix}{row[2]} {row[5]} {row[6]}\n", row[1]


with DataExtractor("analysis/data/zip", "analysis/data/tickers_trade_log", format_row) as extractor:
    extractor.extract_tradelog()
