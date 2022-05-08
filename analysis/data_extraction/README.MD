1) положить zip файлы в `analysis/data/zip`
2) написать нужные тикеры через пробелы в `analysis/data_extraction/allowed_tickers.txt`
3) создать папку `analysis/data/tickers_trade_log/cache`

`extract_trade_log.py` (запускать из корня репозитория) извлекает TradeLog (рыночные сделки) из zip-файлов по каждому тикеру `ticker` и кладет ее
в `analysis/data/ticker_trade_log/ticker.txt` построчно через пробел в формате:

дата в формате `%Y%m%d%H%M%S`, цена, объем
