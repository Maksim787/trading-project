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
        :param format_row: функция (строка в виде списка, дата в формате %Y%m%d) -> (новая строка, тикер)
        :param extract_files: имена файлов, которые нужно распаковать (None для распаковки всех)
        """
        self._dst_directory = dst_directory
        self._zip_directory = zip_directory
        if extract_files is None:
            extract_files = os.listdir(f"{zip_directory}")
        self._zip_files = sorted([os.path.join(zip_directory, x) for x in extract_files])
        self._format_row = format_row
        self._files_by_ticker = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for ticker, file in self._files_by_ticker.items():
            file.close()

    def extract_orderlog(self):
        self._extract_log("OrderLog")

    def extract_tradelog(self):
        self._extract_log("TradeLog")

    def _extract_log(self, log_name: str):
        assert log_name in ["TradeLog", "OrderLog"]
        for zip_file in tqdm(self._zip_files):
            try:
                with zipfile.ZipFile(zip_file, "r") as zip_ref:
                    files = zip_ref.namelist()
                    assert len(files) == 2
                    log = next(filter(lambda x: x.startswith(log_name), files))
                    date = int(zip_file.removeprefix(os.path.join(self._zip_directory, "OrderLog")).removesuffix(".zip"))
                    file = zip_ref.open(log)
                    self._read_file(file, date)
                    file.close()
            except zipfile.BadZipFile:
                print(f"[ERROR] Не удалось считать {zip_file}")

    def _read_file(self, file, date: int):
        reader = csv.reader(TextIOWrapper(file, "utf-8"))
        next(reader)
        for row in reader:
            row_ticker = self._format_row(row, date)
            if row_ticker is not None:
                row, ticker = row_ticker
                write_file = self._files_by_ticker.get(ticker)
                if write_file is None:
                    write_file = open(os.path.join(self._dst_directory, f"{ticker}.txt"), "w")
                    self._files_by_ticker[ticker] = write_file
                write_file.write(row)
