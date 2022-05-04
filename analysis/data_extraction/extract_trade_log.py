from analysis.data_extraction.data_extractor import DataExtractor
from typing import Union

with open("analysis/data_extraction/allowed_tickers.txt") as f:
    allowed_tickers = f.read().split()


def format_row(row: list[str], date: int) -> Union[tuple[str, str], None]:
    # row = [TRADENO, SECCODE, TIME, BUYORDERNO, SELLORDERNO, PRICE, VOLUME]
    # return (time, price, volume)
    if row[1] not in allowed_tickers:
        return None
    assert len(row[2]) == 6
    return " ".join([str(int(row[2]) + date * 10 ** 6), row[5], row[6], "\n"]), row[1]


extractor = DataExtractor("analysis/data/zip", "analysis/data/tickers_trade_log", format_row)
extractor.extract_tradelog()
