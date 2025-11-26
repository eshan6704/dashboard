# indicater.py
import pandas as pd
import numpy as np
import talib

def calculate_indicators(df):
    """
    Calculate multiple indicators for given OHLCV df.
    Returns dict of indicator name -> DataFrame/Series.
    """
    indicators = {}

    close = df['Close'].astype(float)
    high = df['High'].astype(float)
    low = df['Low'].astype(float)
    volume = df['Volume'].astype(float)

    # --- MA on main chart ---
    indicators['SMA20'] = talib.SMA(close, timeperiod=20)
    indicators['SMA50'] = talib.SMA(close, timeperiod=50)

    # --- MACD ---
    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    indicators['MACD'] = pd.DataFrame({'MACD': macd, 'Signal': macdsignal, 'Hist': macdhist})

    # --- RSI ---
    indicators['RSI'] = talib.RSI(close, timeperiod=14)

    # --- SuperTrend (not in TA-Lib, custom function) ---
    indicators['SuperTrend'] = supertrend(high, low, close, period=10, multiplier=3)

    return indicators

def supertrend(high, low, close, period=10, multiplier=3):
    """
    Simple SuperTrend implementation.
    Returns Series with trend value.
    """
    atr = talib.ATR(high, low, close, timeperiod=period)
    hl2 = (high + low) / 2
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)
    trend = pd.Series(index=close.index)
    direction = True  # True = uptrend

    for i in range(len(close)):
        if i == 0:
            trend.iloc[i] = final_upperband.iloc[i]
        else:
            if close.iloc[i] > final_upperband.iloc[i-1]:
                direction = True
            elif close.iloc[i] < final_lowerband.iloc[i-1]:
                direction = False
            if direction:
                trend.iloc[i] = final_lowerband.iloc[i]
            else:
                trend.iloc[i] = final_upperband.iloc[i]

    return trend
