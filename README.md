# trading-project

## Использование тестера

```python
from data.getter import DataGetter
from testing.tester import Tester
from evaluate.result import TestResult
from strategy.random_strategy import RandomStrategy

tester = Tester(DataGetter(), TestResult)
result = tester.test(RandomStrategy("SBER.ME"))
result.plot_capital()
```

```Tester``` принимает в конструкторе:
1. ```data_getter``` - объект класса, имеющего метод ```get_stock(self, stock_name: str, start: str, end: str, interval: str) -> list[float]```, который получает данные
2. ```result_class``` - объект класса, который будет обрабатывать результаты стратегии

```Tester``` имеет метод ```test(self, strategy: BaseStrategy)```, тестирующий стратегию и возвращающий объект класса ```result_class```

## Написание стратегий

Стратегия наследуется от базового класса ```BaseStrategy``` и зовет его конструктор

В конструкторе нужно переопределить поля — настройки стратегии. 

Настройки:
1. ```needed_stocks``` - список названий котировок, которые использует стратегия
2. ```start``` и ```end``` - строчки начала и конца периода тестирования стратегии
3. ```interval``` - интервал между наблюдением цен: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

Пример конструктора:

```python
def __init__(self, stock_name, initial_money=1e6):
    super().__init__(initial_money)
    self.needed_stocks.append(stock_name)
    self.start = "2020-01-01"
    self.end = "2021-01-01"
    self.interval = "1d"
```

Стратегия должна переопределять метод ```make_tick(self)```, который создает ордера (покупка или продажа выбранных инструментов).
Далее описывается, что доступно стратегии в этом методе.

Доступен метод ```create_order(self, stock_name: str, is_buy: Union[bool, int], number: int, duration=None)```. Создает объект класса ```Order```.

1. ```stock_name``` - название инструмента
2. ```is_buy``` - является ли ордером на покупку
3. ```number``` - число акций
4. ```duration``` - число периодов, через которое нужно закрыть ордер (можно не указывать, тогда ордер будет бессрочным)

Доступны поля, которые можно читать, но нельзя изменять:

1. ```orders``` - словарь, по ```id``` ордера возвращает сам ```Order```
2. ```price_history``` - словарь, по названию инструмента возвращает список его цен — историю цен
3. ```capital``` - словарь, по названию инструмента возвращает его количество на счету. Имеет специальный инструмент "money"
4. ```tick``` - счетчик периодов с момента начала тестирования

Ордеры из ```orders``` можно закрывать. У ```Order``` есть метод ```close(self)```, который закрывает позицию
