from tester_trade_log.tester import Indicator, Strategy
from collections import deque


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
        self._history_of_prices = deque()
        self._history_of_volume = deque()
        self._sma_numerator = 0
        self._sma_denominator = 0
        self._num_of_time_slot = 0
        self._new_price = 0
        self._new_volume = 0
        self._total_tact = tact * len_of_window

    def compute_indicator(self, price: int, volume: int, time: int):
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

    def on_finish(self, day: int):
        self._num_of_time_slot = 1
        self._history_of_prices.clear()
        self._history_of_volume.clear()
        self._new_price = 0
        self._new_volume = 0

    def get_activation_time(self):
        return self._wait * self._tact * self._len_of_window

    def get_value(self):
        assert self._wait is False or self._num_of_time_slot > self._total_tact and self._sma_denominator > 0
        return self._sma_numerator / self._sma_denominator


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
        self._ema = 0
        self._num_of_time_slot = 0
        pass

    def compute_indicator(self, price: int, volume: int, time: int):
        self._num_of_time_slot += 1
        if self._num_of_time_slot % self._tact == 0:
            self._ema = price * self.k + self._ema * (1 - self._k)

    def on_finish(self, day: int):
        self._ema = 0
        self._num_of_time_slot = 0
        pass

    def get_activation_time(self):
        return self._time * self._tact
        pass

    def get_value(self):
        return self._ema
        pass


class MACD(Indicator):
    def __init__(self, tact: int, k_long: float, k_short: float, len_of_window: int, wait: bool = True):
        self._tact = tact
        self._long_ema = EMA(tact, k_long)
        self._short_ema = EMA(tact, k_short)
        self._sma = SMA(tact, len_of_window, "simple", wait)
        self._delta = 0

    def compute_indicator(self, price: int, volume: int, time: int):
        self._long_ema.compute_indicator(price, volume, time)
        self._short_ema.compute_indicator(price, volume, time)
        self._delta = self._long_ema.get_value() - self._short_ema.get_value()
        self._sma.compute_indicator(self._delta, volume, time)

    def on_finish(self, day: int):
        self._long_ema.on_finish(day)
        self._short_ema.on_finish(day)
        self._sma.on_finish(day)
        pass

    def get_activation_time(self):
        return self._sma.get_activation_time()

    def get_value(self):
        return self._delta - self._sma.get_value()
