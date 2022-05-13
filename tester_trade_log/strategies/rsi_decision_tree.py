from tester_trade_log.tester import Strategy, Tester
from ta.momentum import RSIIndicator

import datetime
import pickle
import pandas as pd
import numpy as np


class RSITreeStrategy(Strategy):
    def __init__(self, ticker, start_day_index, trading_days, duration):
        self._duration = duration
        self._start_day_index = start_day_index
        self._trading_days = trading_days

        with open(f"tester_trade_log/models/saved/{ticker}", "rb") as f:
            self._model = pickle.load(f)

        def get_model_prediction():
            def rsi_by_length(length, **kwargs):
                return RSIIndicator(pd.Series(kwargs["close"]), length).rsi().values

            def model_prediction(**kwargs):
                X = pd.DataFrame(
                    {
                        "rsi (4 length)": rsi_by_length(4, **kwargs),
                        "rsi (7 length)": rsi_by_length(7, **kwargs),
                        "rsi (14 length)": rsi_by_length(14, **kwargs),
                    }
                )
                nas = np.zeros(13)
                nas.fill(np.nan)
                predictions = np.concatenate((nas, self._model.predict(X.dropna())), axis=0)
                assert len(predictions) == len(kwargs["close"])
                return predictions

            return model_prediction

        self._model_prediction = get_model_prediction()

    def initialize(self, t: "Tester"):
        t.set_period(datetime.timedelta(minutes=1))
        t.set_start_day_index(self._start_day_index)
        t.set_trading_days(self._trading_days)
        t.set_periods_after_start(13)
        t.set_periods_before_finish(self._duration)

        # model prediction indicator
        t.add_indicator(self._model_prediction)

    def on_tick(self, t: "Tester"):
        prediction = t.get_current_indicator(0)
        if not np.isnan(prediction):
            if prediction == 1:
                t.buy(duration=self._duration)
            if prediction == -1:
                t.sell(duration=self._duration)

    def on_start(self, t: "Tester"):
        pass

    def on_finish(self, t: "Tester"):
        pass
