from tester_trade_log.tester import Strategy, Tester
from ta.momentum import RSIIndicator

import datetime
import pickle
import os
import pandas as pd
import numpy as np


class RSITreeStrategy(Strategy):
    def __init__(self, ticker, start_day_index, trading_days, duration, model_path, probability_distance):
        self._duration = duration
        self._start_day_index = start_day_index
        self._trading_days = trading_days
        self._probability_distance = probability_distance

        with open(os.path.join(model_path, ticker), "rb") as f:
            self._model = pickle.load(f)

        def get_model_prediction():
            def rsi_by_length(length, **kwargs):
                return RSIIndicator(pd.Series(kwargs["close"]), length).rsi().values

            def model_prediction(**kwargs):
                lengths = [4, 7, 14]
                X = pd.DataFrame()
                for length in lengths:
                    X[f"rsi ({length} length)"] = rsi_by_length(length, **kwargs)
                nas = np.zeros(max(lengths) - 1)
                nas.fill(np.nan)
                predictions = np.concatenate((nas, self._model.predict_proba(X.dropna())[:, 0].reshape(-1)), axis=0)
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
            # prediction = probability of short
            if abs(prediction - 0.5) >= self._probability_distance:
                if prediction <= 0.5:
                    t.buy(duration=self._duration)
                else:
                    t.sell(duration=self._duration)

    def on_start(self, t: "Tester"):
        pass

    def on_finish(self, t: "Tester"):
        pass
