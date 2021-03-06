# Описание тестера стратегий.

Время делится на периоды. 
За каждый период считается последняя цена сделки и объем.
Эти данные подаются стратегии на вход.
Например, стратегии подаются цены раз в минуту.


Стратегия наследуется от класса ``Strategy``.
В своих методах стратегия принимает объект тестера `t`, у которого можно вызывать методы, начинающиеся на `get` и `set`.
Методы:

1. `initialize()` задает настройки стратегии.
В нем с помощью методов, начинающихся на `set`, можно выставлять: 
- тикер (название инструмента)
- период (например, минута)
- с какого дня начинать тестировать (например, с 0-го)
- сколько дней тестировать (например, 125 дней)
- сколько периодов должно пройти с открытия биржи, чтобы стратегия начала работать
- за сколько периодов до закрытия стратегия должна завершить работу
- добавить индикатор
2. `on_start()` вызывается в начале торгового дня после определенного времени с открытия биржи (которое указывается в `initialize()`)
3. `on_finish()` вызывается в конце торгового дня за определенное время до закрытия биржи (которое указывается в `initialize()`)
4. `on_tick()` вызывается во время работы стратегии на каждый период.
В нем доступны все методы, начинающиеся на `get` и методы для управления позицией:
- `buy(), sell(), open_position()` открывают позицию
(если такая уже есть, то ничего не происходит; если открыта противоположная позиция, то закрывает ее).
`open_position()` - это `buy()` или `sell()` в зависимости от параметра `diration` (`LONG` или `SHORT`).
Методы принимают `duration` - количество периодов, через которое позиция будет закрыта, `stop_loss` и `take_profit`.
- `close_position()` закрывает текущую позицию, если она имеется
- `is_open_position()` возвращает, есть ли сейчас открытая позиция

Также во время и после тестирования можно вызывать у объекта класса `Tester` следующие методы:
1. `get_day_close_price_history()` возвращает цены закрытия по дням
2. `get_trades_history()` возвращает все проведенные сделки по дням (список, каждый элемент которого является списком сделок в день с этим индексом)
3. `get_days_history()` возвращает дни, в которые тестировалась стратегия
4. `get_ticker()` возвращает тикер, на котором тестировалась стратегия

Пример с вызовами некоторых методов тестера можно посмотреть в `tester_trade_log/example/example_strategy.py`

### Работа с индикаторами

Индикатор наследуется от `Indicator` и реализует его методы:

- `get_init_periods()` возвращает количество периодов, необходимых для инициализации индикатора
- `initialize()` инициализирует индикатор, когда прошло ровно `get_init_periods()` периодов.
- `on_tick()` обновляет значение индикатора после поступления информации о новом периоде. 
Отметим, что в тот период, когда зовется `initialize()`, `on_tick()` не вызывается
- `clear()` очищает индикатор в конце дня, чтобы в следующий день опять вызвать `initialize()`

Следующие методы необязательно реализовывать:
- `get_current_value()` возвращает последнее значение индикатора.
  Отметим, что этот метод, как и следующий, может быть вызван сразу после `initialize()`
- `get_values_history()` возвращает всю историю значений индикатора

Пример по работе с индикаторами можно посмотреть в `tester_trade_log/strategies/rsi_strategy.py` 