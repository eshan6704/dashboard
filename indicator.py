# indicater.py
import pandas as pd
import talib as ta

def calculate_indicators(df):
    indicators = {}

    if "Close" in df.columns:
        # Moving averages
        indicators["SMA20"] = ta.SMA(df["Close"], timeperiod=20)
        indicators["SMA50"] = ta.SMA(df["Close"], timeperiod=50)
        indicators["EMA20"] = ta.EMA(df["Close"], timeperiod=20)

        # MACD
        macd, macdsignal, macdhist = ta.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
        indicators["MACD"] = pd.DataFrame({"MACD": macd, "Signal": macdsignal, "Hist": macdhist})

    # SuperTrend as custom
    if all(x in df.columns for x in ["High", "Low", "Close"]):
        indicators["SuperTrend"] = supertrend(df)

    return indicators

def supertrend(df, period=10, multiplier=3):
    import numpy as np
    import talib as ta
    atr = ta.ATR(df["High"], df["Low"], df["Close"], timeperiod=period)
    hl2 = (df["High"] + df["Low"]) / 2
    final_upperband = hl2 + multiplier * atr
    final_lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index, dtype=float)
    trend = True
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > final_upperband.iloc[i-1]:
            trend = True
        elif df["Close"].iloc[i] < final_lowerband.iloc[i-1]:
            trend = False
        st.iloc[i] = final_lowerband.iloc[i] if trend else final_upperband.iloc[i]
    return st
