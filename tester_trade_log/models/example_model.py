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
    rsi = mp.RSIIndicator(df['close'])
    tsi = mp.TSIIndicator(df['close'])
    kama = mp.KAMAIndicator(df['close'])
    roc = mp.ROCIndicator(df['close'])
    srsi = mp.StochRSIIndicator(df['close'])
    ppo = mp.PercentagePriceOscillator(df['close'])
    pvo = mp.PercentageVolumeOscillator(df['close'])

    df['rsi'] = rsi.rsi()
    df['tsi'] = tsi.tsi()
    df['kama'] = kama.kama()
    df['roc'] = roc.roc()
    df['srsi'] = srsi.stochrsi()
    df['ppo'] = ppo.ppo()
    df['pvo'] = pvo.pvo()


def fill_trend_indicators(df):
    aroon = tr.AroonIndicator(df['close'])
    macd = tr.MACD(df['close'])
    ema = tr.EMAIndicator(df['close'])
    sma = tr.SMAIndicator(df['close'], window=7)
    wma = tr.WMAIndicator(df['close'])
    trix = tr.TRIXIndicator(df['close'])
    kst = tr.KSTIndicator(df['close'])
    dpo = tr.DPOIndicator(df['close'])
    stc = tr.STCIndicator(df['close'])

    df['aroon'] = aroon.aroon_indicator()
    df['macd'] = macd.macd()
    df['ema'] = ema.ema_indicator()
    df['sma'] = sma.sma_indicator()
    df['wma'] = wma.wma()
    df['trix'] = trix.trix()
    df['ksti'] = kst.kst()
    df['dpoi'] = dpo.dpo()
    df['stc'] = stc.stc()


def fill_volatility_indicators(df):
    blb = vlt.BollingerBands(df['close'])
    ulc = vlt.UlcerIndex(df['close'])

    df['blb'] = blb.bollinger_hband_indicator()
    df['ulc'] = ulc.ulcer_index()


def fill_volume_indicators(df):
    obv = vlm.OnBalanceVolumeIndicator(df['close'], df['volume'])
    frc = vlm.ForceIndexIndicator(df['close'], df['volume'])
    vpt = vlm.VolumePriceTrendIndicator(df['close'], df['volume'])
    npt = vlm.NegativeVolumeIndexIndicator(df['close'], df['volume'])

    df['obv'] = obv.on_balance_volume()
    df['frc'] = frc.force_index()
    df['vpt'] = vpt.volume_price_trend()
    df['npt'] = npt.negative_volume_index()


def create_old_indicators(df, shift):
    for column in df.columns:
        new_column = 'new_' + column
        df[new_column] = df[column].shift(shift)


class Model:
    def __init__(self, data_directory: str, ticker: str, period: datetime.timedelta, *args, **kwargs):
        self._data_directory = data_directory
        self._ticker = ticker
        self._period = period
        self._df = []
        self._train_data = []
        self._test_data = []
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
        is_first_day = True
        all_data = []
        for day_index, (day, intraday_iterator) in tqdm(data_iterator):
            intraday_history = []
            intraday_price = []
            for i, (time, price, volume) in enumerate(intraday_iterator):
                intraday_history.append([price, volume])
                intraday_price.append(price)
            df = pd.DataFrame(intraday_history, columns=['close', 'volume'])
            fill_momentum_indicators(df)
            fill_trend_indicators(df)
            fill_volatility_indicators(df)
            fill_volume_indicators(df)
            create_old_indicators(df, 1)
            create_old_indicators(df, 5)
            for k in range(horizon):
                intraday_price.append(0)
            df['new_price'] = intraday_price[horizon:]
            df = df.dropna()
            df = df.iloc[head:-(horizon + tail)]
            if is_first_day:
                is_first_day = False
                all_data = df
            else:
                all_data = pd.concat([all_data, df], ignore_index=True)
        print('Creation completed successfully')
        self._df = all_data
        all_data.to_csv(output, sep='\t')

    def fit(self, test_size: int = 0.2):
        self._train_data, self._test_data = train_test_split(self._df, test_size=test_size, shuffle=False)
        # self._tree.fit(self._train_data.drop(['new_price'], axis=1), self._train_data['new_price'])
        self._catboost.fit(self._train_data.drop(['new_price'], axis=1), self._train_data['new_price'])
        print("ALL", self._train_data.shape)

    def predict(self):
        # ans = self._tree.predict_proba(self._test_data.drop(['new_price'], axis=1))
        return self._catboost.score(X=self._test_data.drop(['new_price'], axis=1), y=self._test_data['new_price'])
        # return self._tree.score(self._test_data.drop(['new_price'], axis=1), self._test_data['new_price'])


# p = Model("analysis/data/tickers_trade_log", "SBER", datetime.timedelta(minutes=1), max_depth=6)
p = Model("analysis/data/tickers_trade_log", "GAZP", datetime.timedelta(minutes=1), iterations=2, learning_rate=0.7, depth=2)
lst = []
for i in range(1, 11):
    p.create_data(i, True)
    p.fit()
    lst.append(p.predict())
print(lst)
