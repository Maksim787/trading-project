# trading-project

## Использование тестера

```python
from data.getter import DataGetter
from testing.tester import Tester
from evaluate.result import TestResult
from strategy.random_strategy import RandomStrategy

tester = Tester(DataGetter(), TestResult())
result = tester.test(RandomStrategy("SBER.ME", 1e7))
result.plot_capital()
```

```Tester``` принимает в конструкторе:
1. ```data_getter``` - объект класса, который получает данные
2. ```result_object``` - объект класса, который будет обрабатывать результаты стратегии

```data_getter``` имеет метод ```get_equity(self, equity, start, end, interval)```, получающий данные по нужному инструменту

```result_object``` имеет метод ```initialize(self, capital_history, price_history, tester)```, который обрабатывает результаты стратегии

```Tester``` имеет метод ```test(self, strategy: BaseStrategy)```, тестирующий стратегию и возвращающий проинициализированный ```result_class```

## Написание стратегий

Стратегия наследуется от базового класса ```BaseStrategy``` и зовет его конструктор

Стратегии доступно поле ```self.tester```, с помощью которого осуществляется взаимодействие с тестирующей системой. Стратегия имеет два метода:

I. ```initialize(self)``` - задает настройки стратегии. Доступные функции:

1. ```set_start(start)``` - задает дату начала тестирования
2. ```set_end(start)``` - задает дату конца тестирования
3. ```set_interval(interval)``` - задает интервал между наблюдениями цен: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
4. ```add_equity(equity)``` - добавляет наблюдения за инструментом
5. ```set_cash(cash)``` - задает начальное количество денег

II. ```make_tick(self)``` - создает ордера (покупка или продажа выбранных инструментов). Доступные функции:
1. ```create_order(number, equity, duration=None)``` - делает покупку (```number > 0```) или продажу (```number < 0```) инструмента ```equity```. 
   Если ```duration``` не  ```None```, то позиция будет автоматически закрыта по прошествии ```duration``` периодов. 
   Возвращает ```order_id``` - уникальный идентификатор позиции.
2. ```close_order(order_id)``` - закрывает позицию с идентификатором ```order_id```.  
3. ```close_all_orders()``` - закрывает все позиции.
