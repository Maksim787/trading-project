import os
import zipfile
import csv
from tqdm import tqdm
from io import TextIOWrapper


class DataExtractor:
    def __init__(self, zip_directory: str, dst_directory: str, format_row, extract_files=None):
        """
        :param zip_directory: директория с zip файлами и только ими
        :param dst_directory: директория, в которую нужно распаковать
        :param format_row: функция (строка в виде списка, дата) -> (новая строка, тикер)
        :param extract_files: имена файлов, которые нужно распаковать (None для распаковки всех)
        """
        self._dst_directory = dst_directory
        self._zip_directory = zip_directory
        if extract_files is None:
            extract_files = os.listdir(f"{zip_directory}")
        self._zip_files = sorted([f"{zip_directory}/{x}" for x in extract_files])
        self._format_row = format_row
        self._files_by_ticker = {}
        self._opened_files = []

    def extract_orderlog(self):
        self._extract_log("OrderLog")

    def extract_tradelog(self):
        self._extract_log("TradeLog")

    def _extract_log(self, log_name: str):
        # (int(date), trade_log_file, order_log_file)
        for zip_file in tqdm(self._zip_files):
            try:
                with zipfile.ZipFile(zip_file, "r") as zip_ref:
                    files = zip_ref.namelist()
                    assert len(files) == 2
                    trade_log = next(filter(lambda x: x.startswith("TradeLog"), files))  # trades
                    order_log = next(filter(lambda x: x.startswith("OrderLog"), files))  # orders
                    date = int(zip_file.removeprefix(f"{self._zip_directory}/OrderLog").removesuffix(".zip"))
                    if log_name == "TradeLog":
                        file = zip_ref.open(trade_log)
                    elif log_name == "OrderLog":
                        file = zip_ref.open(order_log)
                    else:
                        raise AssertionError
                    self._read_file(file, date)
                    file.close()
            except zipfile.BadZipFile:
                print(f"[ERROR] Не удалось считать {zip_file}")
        for file in self._opened_files:
            file.close()

    def _read_file(self, file, date: int):
        reader = csv.reader(TextIOWrapper(file, "utf-8"))
        next(reader)
        for row in reader:
            row_ticker = self._format_row(row, date)
            if row_ticker is not None:
                row, ticker = row_ticker
                write_file = self._files_by_ticker.get(ticker)
                if write_file is None:
                    write_file = open(f"{self._dst_directory}/{ticker}.txt", "w")
                    self._opened_files.append(write_file)
                    self._files_by_ticker[ticker] = write_file
                write_file.write(row)
