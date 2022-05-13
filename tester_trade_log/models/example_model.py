from catboost import CatBoostRegressor
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
    df['rsi'] = mp.RSIIndicator(df['close']).rsi()
    df['tsi'] = mp.TSIIndicator(df['close']).tsi()
    df['kama'] = mp.KAMAIndicator(df['close']).kama()
    df['roc'] = mp.ROCIndicator(df['close']).roc()
    df['srsi'] = mp.StochRSIIndicator(df['close']).stochrsi()
    df['ppo'] = mp.PercentagePriceOscillator(df['close']).ppo()
    df['pvo'] = mp.PercentageVolumeOscillator(df['close']).pvo()


def fill_trend_indicators(df):
    df['aroon'] = tr.AroonIndicator(df['close']).aroon_indicator()
    df['macd'] = tr.MACD(df['close']).macd()
    df['ema'] = tr.EMAIndicator(df['close']).ema_indicator()
    df['sma'] = tr.SMAIndicator(df['close'], window=7).sma_indicator()
    df['wma'] = tr.WMAIndicator(df['close']).wma()
    df['trix'] = tr.TRIXIndicator(df['close']).trix()
    df['ksti'] = tr.KSTIndicator(df['close']).kst()
    df['dpoi'] = tr.DPOIndicator(df['close']).dpo()
    df['stc'] = tr.STCIndicator(df['close']).stc()


def fill_volatility_indicators(df):
    df['blb'] = vlt.BollingerBands(df['close']).bollinger_hband_indicator()
    df['ulc'] = vlt.UlcerIndex(df['close']).ulcer_index()


def fill_volume_indicators(df):
    df['obv'] = vlm.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
    df['frc'] = vlm.ForceIndexIndicator(df['close'], df['volume']).force_index()
    df['vpt'] = vlm.VolumePriceTrendIndicator(df['close'], df['volume']).volume_price_trend()
    df['npt'] = vlm.NegativeVolumeIndexIndicator(df['close'], df['volume']).negative_volume_index()


def create_old_indicators(df, shift):
    for column in df.columns:
        new_column = 'new_' + str(shift) + '_' + column
        df[new_column] = df[column].shift(shift)


class Model:
    def __init__(self, data_directory: str, ticker: str, period: datetime.timedelta, *args, **kwargs):
        self._data_directory = data_directory
        self._ticker = ticker
        self._period = period
        self._df = []
        self._train_data = []
        self._test_data = []
        self._count_of_days = 0
        self._test_size = 0
        # self._tree = DecisionTreeClassifier(*args, **kwargs)
        # self._tree = DecisionTreeRegressor(*args, **kwargs)
        self._catboost = CatBoostRegressor(*args, **kwargs)
        pass

    def create_data(self, horizon: int, refill: bool = False, head: int = 20, tail: int = 10):
        output = "analysis/data/indicator_data/" + self._ticker + '_' + str(self._period.total_seconds()) + '_' + str(
            horizon) + '.csv'
        if os.path.exists(output) and refill is False:
            self._df = pd.read_csv(output, sep='\t')
            print("Already exist")
            return
        data_iterator = enumerate(DataIterator(self._data_directory, self._ticker, self._period))
        lst_of_df = []
        for day_index, (day, intraday_iterator) in tqdm(data_iterator):
            intraday_history = []
            intraday_price = []
            for i, (time, price, high, low, volume) in enumerate(intraday_iterator):
                intraday_history.append([price, volume])
                intraday_price.append(price)
            df = pd.DataFrame(intraday_history, columns=['close', 'volume'])
            fill_momentum_indicators(df)
            fill_trend_indicators(df)
            fill_volatility_indicators(df)
            fill_volume_indicators(df)
            lst_of_times = [1, 5]
            for hor in lst_of_times:
                create_old_indicators(df, hor)
            for k in range(horizon):
                intraday_price.append(0)
            df['new_price'] = intraday_price[horizon:]
            df['day'] = day_index
            df = df.dropna()
            df = df.iloc[head:-(horizon + tail)]
            lst_of_df.append(df)
        all_data = pd.concat(lst_of_df, ignore_index=True)
        print('Creation completed successfully')
        self._df = all_data
        all_data.to_csv(output, sep='\t')

    def fit(self, test_size: int = 0.2):
        self._count_of_days = max(self._df['day'])
        self._test_size = test_size
        # todo self._train_data = df[where df[days] < (1 - test_size) * count_of_days]
        print(self._count_of_days)
        self._train_data = self._df[self._df['day'] < (1 - self._test_size) * self._count_of_days].drop(['day'], axis=1)
        # self._tree.fit(self._train_data.drop(['new_price'], axis=1), self._train_data['new_price'])
        self._catboost.fit(self._train_data.drop(['new_price'], axis=1), self._train_data['new_price'])
        print("ALL", self._train_data.shape)

    def predict(self):
        self._test_data = self._df[self._df['day'] > (1 - self._test_size) * self._count_of_days].drop(['day'], axis=1)
        # ans = self._tree.predict_proba(self._test_data.drop(['new_price'], axis=1))
        return self._catboost.score(X=self._test_data.drop(['new_price'], axis=1), y=self._test_data['new_price'])
        # return self._tree.score(self._test_data.drop(['new_price'], axis=1), self._test_data['new_price'])


# p = Model("analysis/data/tickers_trade_log", "SBER", datetime.timedelta(minutes=1), max_depth=6)
p = Model("analysis/data/tickers_trade_log", "SBER", datetime.timedelta(minutes=1), iterations=2, learning_rate=0.7,
          depth=2)
lst = []
for i in range(1, 4):
    p.create_data(i)
    p.fit()
    lst.append(p.predict())
print(lst)
