from tester_trade_log.tester import Indicator, Tester
from collections import deque


class RSI(Indicator):
    def __init__(self, length):
        self._length = length
        self._changes_queue = deque()
        self._total_sum = 0
        self._positive_sum = 0
        self._last_price = None
        self._rsi_history = []

    def get_init_periods(self) -> int:
        return self._length

    def initialize(self, t: "Tester"):
        prices = t.get_today_price_history()
        assert len(prices) == self._length
        self._last_price = prices[-1]
        changes = np.diff(prices)
        self._changes_queue = deque(map(float, changes))
        self._total_sum = float(np.abs(changes).sum())
        self._positive_sum = float(changes[changes > 0].sum())
        self._rsi_history.append(self.get_current_value())

    def on_tick(self, t: "Tester"):
        new_price = t.get_current_price()
        new_change = new_price - self._last_price
        self._last_price = new_price
        old_change = self._changes_queue.popleft()
        self._changes_queue.append(new_change)
        self._total_sum += abs(new_change) - abs(old_change)
        if new_change > 0:
            self._positive_sum += new_change
        if old_change > 0:
            self._positive_sum -= old_change
        self._rsi_history.append(self.get_current_value())

    def get_current_value(self):
        return self._positive_sum / self._total_sum * 100 if self._total_sum else 50

    def get_values_history(self):
        return self._rsi_history

    def clear(self, t: "Tester"):
        self._rsi_history.clear()
        self._last_price = None


class SMA(Indicator):
    def __init__(self, tact: int, len_of_window: int, mode: str = "simple", wait: bool = True):
        """
        :param tact: Сколько временных промежутков нужно будет ждать, чтобы индикатор обновился
        :param len_of_window: Сколько элементов содержит временное окно
        :param mode: Поддерживается 2 режима, simple(MEAN of CLOSE) и volume(MEAN of VOLUME * CLOSE)
        :param wait: Нужно ли ждать до заполнения индикатора
        """
        assert len_of_window > 1
        self._tact = tact
        self._len_of_window = len_of_window
        self._mode = mode
        self._wait = wait
        self._history = list()
        self._memory_of_prices = deque()
        self._memory_of_volume = deque()
        self._sma_numerator = 0
        self._sma_denominator = 0
        self._num_of_time_slot = 0
        self._new_price = 0
        self._new_volume = 0
        self._total_tact = tact * len_of_window

    def initialize(self, t: "Tester"):
        # todo Запихать начальные данные
        pass

    def on_tick(self, t: "Tester"):
        self.compute_indicator(t.get_current_price(), t.get_current_volume(), t.get_current_time())

    def compute_indicator(self, price: int, volume: int):
        self._num_of_time_slot += 1
        self._new_price = price
        self._new_volume += volume
        if self._num_of_time_slot % self._tact == 0:
            if self._mode == "simple":
                if self._num_of_time_slot > self._total_tact:
                    self._sma_numerator -= self._history_of_prices.popleft()
                self._sma_denominator = self._len_of_window
                self._sma_numerator += self._new_price
            elif self._mode == "volume":
                if self._num_of_time_slot > self._total_tact:
                    last_price = self._history_of_prices.popleft()
                    last_volume = self._history_of_volume.popleft()
                    self._sma_denominator -= last_volume
                    self._sma_numerator -= last_price * last_volume
                self._sma_denominator += self._new_volume
                self._sma_numerator += self._new_price * self._new_volume
            self._history_of_prices.append(self._new_price)
            self._history_of_volume.append(self._new_volume)
            self._new_price = 0
            self._new_volume = 0
            self._sma_numerator = 0
            self._sma_denominator = 0
        pass

    def clear(self, t: "Tester"):
        self._num_of_time_slot = 1
        self._history = []
        self._memory_of_prices.clear()
        self._memory_of_volume.clear()
        self._new_price = 0
        self._new_volume = 0

    def get_init_periods(self):
        return self._wait * self._tact * self._len_of_window

    def get_current_value(self):
        assert self._wait is False or self._num_of_time_slot > self._total_tact and self._sma_denominator > 0
        return self._sma_numerator / self._sma_denominator

    def get_values_history(self):
        return self._history


class EMA(Indicator):
    def __init__(self, tact: int, k: float, time: int = 0):
        """

        :param tact:  Сколько временных промежутков нужно будет ждать, чтобы индикатор обновился
        :param k: Параметр в формуле EMA_new = PRICE_new * k + EMA * (1-k)
        :param time: Скольно нужно ждать временных периодов для начала действия индикатора
        """
        self._tact = tact
        self._k = k
        self._time = time
        self._history = []
        self._ema = 0
        self._num_of_time_slot = 0
        pass

    def initialize(self, t: "Tester"):
        # todo Инициализировать данные на старте
        pass

    def on_tick(self, t: "Tester"):
        self._num_of_time_slot += 1
        if self._num_of_time_slot % self._tact == 0:
            self._ema = t.get_current_price() * self.k + self._ema * (1 - self._k)
            self._history.append(self._ema)

    def clear(self, t: "Tester"):
        self._ema = 0
        self._num_of_time_slot = 0
        self._history.clear()

    def get_init_periods(self):
        return self._time * self._tact

    def get_current_value(self):
        return self._ema

    def get_values_history(self):
        return self._history


class MACD(Indicator):
    def __init__(self, tact: int, k_long: float, k_short: float, len_of_window: int, wait: bool = True):
        self._tact = tact
        self._long_ema = EMA(tact, k_long)
        self._short_ema = EMA(tact, k_short)
        self._sma = SMA(tact, len_of_window, "simple", wait)
        self._delta = 0

    def initialize(self, t: "Tester"):
        pass

    def on_tick(self, t: "Tester"):
        self._long_ema.on_tick(t)
        self._short_ema.on_tick(t)
        self._delta = self._long_ema.get_current_value() - self._short_ema.get_current_value()
        self._sma.compute_indicator(self._delta, t.get_current_volume())

    def clear(self, t: "Tester"):
        self._long_ema.clear(t)
        self._short_ema.clear(t)
        self._sma.clear(t)
        pass

    def get_init_periods(self):
        return self._sma.get_init_periods()

    def get_current_value(self):
        return self._delta - self._sma.get_current_value()

    def get_values_history(self):
        return
        pass
