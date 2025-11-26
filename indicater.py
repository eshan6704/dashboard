# indicater.py
import pandas as pd
import talib
import numpy as np

def calculate_indicators(df):
    """
    Calculate all possible indicators from TA-Lib for a given OHLCV DataFrame.
    df: DataFrame with columns ['Open','High','Low','Close','Volume']
    Returns: dict of {indicator_name: Series or DataFrame}
    """
    indicators = {}
    
    close = df['Close']
    high = df['High']
    low = df['Low']
    open_ = df['Open']
    volume = df['Volume']

    # --- Moving Averages ---
    indicators['SMA_5'] = talib.SMA(close, timeperiod=5)
    indicators['SMA_10'] = talib.SMA(close, timeperiod=10)
    indicators['SMA_20'] = talib.SMA(close, timeperiod=20)
    indicators['SMA_50'] = talib.SMA(close, timeperiod=50)
    indicators['EMA_5'] = talib.EMA(close, timeperiod=5)
    indicators['EMA_10'] = talib.EMA(close, timeperiod=10)
    indicators['EMA_20'] = talib.EMA(close, timeperiod=20)
    indicators['EMA_50'] = talib.EMA(close, timeperiod=50)

    # --- Trend Indicators ---
    indicators['ADX'] = talib.ADX(high, low, close, timeperiod=14)
    indicators['CCI'] = talib.CCI(high, low, close, timeperiod=14)
    indicators['AROON_UP'], indicators['AROON_DOWN'] = talib.AROON(high, low, timeperiod=14)
    indicators['MACD'], indicators['MACD_signal'], indicators['MACD_hist'] = talib.MACD(close)
    indicators['ATR'] = talib.ATR(high, low, close, timeperiod=14)

    # --- Oscillators ---
    indicators['RSI'] = talib.RSI(close, timeperiod=14)
    indicators['STOCH_slowk'], indicators['STOCH_slowd'] = talib.STOCH(high, low, close)
    indicators['STOCHF_fastk'], indicators['STOCHF_fastd'] = talib.STOCHF(high, low, close)
    indicators['WILLR'] = talib.WILLR(high, low, close, timeperiod=14)

    # --- Volatility ---
    indicators['BB_upper'], indicators['BB_middle'], indicators['BB_lower'] = talib.BBANDS(close)
    indicators['ATR'] = talib.ATR(high, low, close, timeperiod=14)

    # --- Fallback for SuperTrend ---
    try:
        indicators['SuperTrend'] = supertrend(df)
    except Exception as e:
        indicators['SuperTrend'] = pd.Series([np.nan]*len(df), index=df.index)

    return indicators


def supertrend(df, period=10, multiplier=3):
    """
    Compute SuperTrend indicator.
    Returns a Series same length as df with SuperTrend values.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']

    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    supertrend = pd.Series(index=df.index)
    direction = True  # True = bullish

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = hl2.iloc[i]
            continue
        if close.iloc[i] > supertrend.iloc[i-1]:
            direction = True
        elif close.iloc[i] < supertrend.iloc[i-1]:
            direction = False

        if direction:
            supertrend.iloc[i] = lowerband.iloc[i] if lowerband.iloc[i] > supertrend.iloc[i-1] else supertrend.iloc[i-1]
        else:
            supertrend.iloc[i] = upperband.iloc[i] if upperband.iloc[i] < supertrend.iloc[i-1] else supertrend.iloc[i-1]

    return supertrend
