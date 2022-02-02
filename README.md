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

```data_getter``` имеет метод ```get_equity(self, equity, start, end, interval)```, получающий данные по нужному активу за определенный период с нужной частотой

```result_object``` имеет метод ```initialize(self, capital_history, price_history, tester)```, который обрабатывает результаты стратегии

```Tester``` имеет метод ```test(self, strategy)```, тестирующий стратегию и возвращающий проинициализированный ```result_class```

## Написание стратегий

Стратегия наследуется от базового класса ```BaseStrategy``` и зовет его конструктор

Взаимодействие с тестирующей системой осуществляется через параметр ```t: Tester```. 

I. ```initialize(self, t: Tester)``` — задает настройки стратегии. Доступные методы у ```t: Tester```:

1. ```set_start(start)```
1. ```set_end(start)```
1. ```set_interval(interval)```
1. ```set_cash(cash)```
1. ```add_equity(equity)```

II. ```make_tick(self, t: Tester)``` — покупает и продает активы, создает позиции. Доступные методы у ```t: Tester```:
1. ```get_start() -> datetime.date```
1. ```get_end() -> datetime.date```
1. ```get_tick() -> int```
1. ```get_total_ticks() -> int```
1. ```get_cash() -> float```
1. ```get_equity(equity: str) -> float```
1. ```get_capital() -> dict[str, float]```
1. ```get_price(equity: str) -> float```
1. ```get_prices() -> dict[str, float]```
1. ```get_capital_history() -> dict[str, list[float]]```
1. ```get_equity_price_history(equity: str) -> list[float]```
1. ```get_price_history() -> dict[str, list[float]]```
1. ```get_order(order_id: int) -> Order```
1. ```buy_equity(number: int, equity: str)```
1. ```sell_equity(number: int, equity: str)```
1. ```create_order(number: int, equity: str, duration=None) -> int```
1. ```close_order(order_id: int)```
1. ```close_all_orders()```

В методе ```make_tick``` можно получать разные данные об истории цен и истории своего капитала,
покупать и продавать активы, создавать позиции.
Позиция — объект класса ```Order```, которая содержит название актива,
количество покупаемого актива (отрицательное для продажи),
уникальный id позиции и количество периодов, через которое она будет закрыта. 