# trading-project

## Использование тестирующей системы

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

```Tester``` имеет метод ```test(self, strategy)```, тестирующий стратегию и возвращающий проинициализированный ```result_class```

## Написание стратегий

Стратегия наследуется от базового класса ```BaseStrategy``` и зовет его конструктор

Взаимодействие с тестирующей системой осуществляется через параметр ```t: Tester```. 

I. ```initialize(self, t)``` - задает настройки стратегии. Доступные методы у ```t: Tester```:

1. ```set_start(start)``` - задает дату начала тестирования
1. ```set_end(start)``` - задает дату конца тестирования
1. ```set_interval(interval)``` - задает интервал между наблюдениями цен: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
1. ```add_equity(equity)``` - добавляет наблюдения за инструментом
1. ```set_cash(cash)``` - задает начальное количество денег

II. ```make_tick(self, t)``` - создает ордера (покупка или продажа выбранных инструментов). Доступные методы у ```t: Tester```:
1. ```buy_equity(number: int, equity)``` - покупает ```number``` инструмента ```equity``` (если ```number < 0```, то продает)
1. ```sell_equity(number: int, equity)``` - продает ```number``` инструмента ```equity``` (если ```number < 0```, то покупает)
1. ```create_order(number, equity, duration=None)``` - делает покупку (```number > 0```) или продажу (```number < 0```) инструмента ```equity```. 
   Если ```duration``` не  ```None```, то позиция будет автоматически закрыта по прошествии ```duration``` периодов. 
   Возвращает ```order_id``` - уникальный идентификатор позиции.
1. ```close_order(order_id)``` - закрывает позицию с идентификатором ```order_id```.  
1. ```close_all_orders()``` - закрывает все позиции.
