from catboost import CatBoostRegressor, CatBoostClassifier
import datetime
import pandas as pd
from ta import momentum as mp
from ta import trend as tr
from ta import volatility as vlt
from ta import volume as vlm
from tester_trade_log.data_iterator import DataIterator
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
import os.path


def fill_momentum_indicators(df):
    df["rsi"] = mp.RSIIndicator(df["close"]).rsi()
    df["tsi"] = mp.TSIIndicator(df["close"]).tsi()
    df["kama"] = mp.KAMAIndicator(df["close"]).kama()
    df["roc"] = mp.ROCIndicator(df["close"]).roc()
    df["srsi"] = mp.StochRSIIndicator(df["close"]).stochrsi()
    df["ppo"] = mp.PercentagePriceOscillator(df["close"]).ppo()
    df["pvo"] = mp.PercentageVolumeOscillator(df["close"]).pvo()


def fill_trend_indicators(df):
    df["aroon"] = tr.AroonIndicator(df["close"]).aroon_indicator()
    df["macd"] = tr.MACD(df["close"]).macd()
    df["ema"] = tr.EMAIndicator(df["close"]).ema_indicator()
    df["sma"] = tr.SMAIndicator(df["close"], window=7).sma_indicator()
    df["wma"] = tr.WMAIndicator(df["close"]).wma()
    df["trix"] = tr.TRIXIndicator(df["close"]).trix()
    df["ksti"] = tr.KSTIndicator(df["close"]).kst()
    df["dpoi"] = tr.DPOIndicator(df["close"]).dpo()
    df["stc"] = tr.STCIndicator(df["close"]).stc()


def fill_volatility_indicators(df):
    df["blb"] = vlt.BollingerBands(df["close"]).bollinger_hband_indicator()
    df["ulc"] = vlt.UlcerIndex(df["close"]).ulcer_index()


def fill_volume_indicators(df):
    df["obv"] = vlm.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()
    df["frc"] = vlm.ForceIndexIndicator(df["close"], df["volume"]).force_index()
    df["vpt"] = vlm.VolumePriceTrendIndicator(df["close"], df["volume"]).volume_price_trend()
    df["npt"] = vlm.NegativeVolumeIndexIndicator(df["close"], df["volume"]).negative_volume_index()


def create_old_indicators(df, shifts):
    for column in df.columns:
        for shift in shifts:
            new_column = "new_" + str(shift) + "_" + column
            df[new_column] = df[column].shift(shift)


class Model:
    def __init__(self, data_directory: str, ticker: str, period: datetime.timedelta, type_of_model: str, model):
        """

        :param data_directory: Где лежат данные
        :param ticker: Тикер, на котором играет модель
        :param period: Раз во сколько идет обновление данных
        :param type_of_model: Какую именно задачу выполняет модель ("regressor"/"classificator")
        :param model: Непосредственно сама модель
        """
        self._data_directory = data_directory
        self._ticker = ticker
        self._period = period
        self._df = []
        self._train_data = []
        self._test_data = []
        self._alpha = 0
        self._count_of_days = 0
        self._test_size = 0
        self._type_of_model = type_of_model
        self._model = model
        pass

    def _compute_classificator(self, change):
        if change > self._alpha * self.std:
            return 1
        elif change < self._alpha * self.std:
            return -1
        return 0

    def create_data(self, horizon: int, alpha: float, refill: bool = False, head: int = 20, tail: int = 10):
        self._alpha = alpha
        output = "analysis/data/indicator_data/" + self._ticker + "_" + str(self._period.total_seconds()) + "_" + str(
            horizon) + ".csv"
        if os.path.exists(output) and refill is False:
            self._df = pd.read_csv(output, sep="\t")
            print(self._df.columns)
            print("Already exist")
            return
        data_iterator = enumerate(DataIterator(self._data_directory, self._ticker, self._period))
        lst_of_df = []
        for day_index, (day, intraday_iterator) in tqdm(data_iterator):
            intraday_history = []
            intraday_price = []
            for i, (time, price, high, low, volume) in enumerate(zip(*intraday_iterator)):
                intraday_history.append([price, volume])
                intraday_price.append(price)
            df = pd.DataFrame(intraday_history, columns=["close", "volume"])
            fill_momentum_indicators(df)
            fill_trend_indicators(df)
            fill_volatility_indicators(df)
            fill_volume_indicators(df)
            lst_of_times = [1, 5]
            create_old_indicators(df, lst_of_times)
            for k in range(horizon):
                intraday_price.append(0)
            df["new_price"] = intraday_price[horizon:]
            # df["price_change"] = df["new_price"] - df["price_change"]
            df["trand_of_price"] = (df["new_price"] > df["close"]).astype(bool)
            df["day"] = day_index
            df = df.dropna()
            df = df.iloc[head: -(horizon + tail)]
            lst_of_df.append(df)
        all_data = pd.concat(lst_of_df, ignore_index=True)
        # df["trand_of_price"] = df["trand_of_price"].apply(self._compute_classificator)
        print("Creation completed successfully")
        self._df = all_data
        all_data.to_csv(output, sep="\t")

    def fit(self, test_size: int = 0.2):
        self._count_of_days = max(self._df["day"])
        self._test_size = test_size
        self._train_data = self._df[self._df["day"] < (1 - self._test_size) * self._count_of_days].drop(["day"], axis=1)
        if self._type_of_model == "regressor":
            self._model.fit(self._train_data.drop(["new_price", "trand_of_price"], axis=1),
                            self._train_data["new_price"])
        elif self._type_of_model == "classificator":
            self._model.fit(self._train_data.drop(["new_price", "trand_of_price"], axis=1),
                            self._train_data["trand_of_price"])
        print("ALL", self._train_data.shape)

    def get_score(self):
        self._test_data = self._df[self._df["day"] >= (1 - self._test_size) * self._count_of_days].drop(["day"], axis=1)
        if self._type_of_model == "regressor":
            return self._model.score(self._test_data.drop(['new_price', 'trand_of_price'], axis=1),
                                     self._test_data['new_price'])
        elif self._type_of_model == "classificator":
            return self._model.score(self._test_data.drop(['new_price', 'trand_of_price'], axis=1),
                                     self._test_data['trand_of_price'])


p = Model("analysis/data/tickers_trade_log", "SIBN", datetime.timedelta(minutes=1), "classificator",
          DecisionTreeClassifier(max_depth=2))
'''p = Model("analysis/data/tickers_trade_log", "SBER", datetime.timedelta(minutes=1), "classificator",
          CatBoostClassifier(iterations=2, learning_rate=0.7, depth=2))'''
# p = Model("analysis/data/tickers_trade_log", "SBER", datetime.timedelta(minutes=1), iterations=2, learning_rate=0.7, depth=2)
lst = []
for i in range(1, 5):
    p.create_data(i, 0.5)
    p.fit()
    lst.append(p.get_score())
print(lst)
