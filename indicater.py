# indicater.py
import pandas as pd
import numpy as np
import talib

# -------------------------------
# Custom SuperTrend implementation
# -------------------------------
def supertrend(df, period=10, multiplier=3):
    """
    Compute SuperTrend
    """
    hl2 = (df['High'] + df['Low']) / 2
    atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
    
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    
    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = upperband.iloc[i]
            direction.iloc[i] = 1
            continue
        if df['Close'].iloc[i] > supertrend.iloc[i-1]:
            direction.iloc[i] = 1
            supertrend.iloc[i] = lowerband.iloc[i]
        elif df['Close'].iloc[i] < supertrend.iloc[i-1]:
            direction.iloc[i] = -1
            supertrend.iloc[i] = upperband.iloc[i]
        else:
            direction.iloc[i] = direction.iloc[i-1]
            supertrend.iloc[i] = supertrend.iloc[i-1]
    return supertrend

# -------------------------------
# Main indicator calculation
# -------------------------------
def calculate_indicators(df):
    """
    Compute major TA-Lib indicators and custom indicators.
    Return dictionary {indicator_name: series_or_df}
    """
    indicators = {}

    # --- Price-based moving averages ---
    indicators['SMA5'] = talib.SMA(df['Close'], timeperiod=5)
    indicators['SMA20'] = talib.SMA(df['Close'], timeperiod=20)
    indicators['SMA50'] = talib.SMA(df['Close'], timeperiod=50)
    indicators['SMA200'] = talib.SMA(df['Close'], timeperiod=200)
    
    indicators['EMA5'] = talib.EMA(df['Close'], timeperiod=5)
    indicators['EMA20'] = talib.EMA(df['Close'], timeperiod=20)
    indicators['EMA50'] = talib.EMA(df['Close'], timeperiod=50)
    indicators['EMA200'] = talib.EMA(df['Close'], timeperiod=200)

    # --- Momentum indicators ---
    indicators['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    indicators['STOCH'], indicators['STOCH_signal'] = talib.STOCH(
        df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0,
        slowd_period=3, slowd_matype=0
    )
    indicators['MACD'], indicators['MACD_signal'], indicators['MACD_hist'] = talib.MACD(df['Close'])
    indicators['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    indicators['CCI'] = talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=14)
    indicators['OBV'] = talib.OBV(df['Close'], df['Volume'])

    # --- Volatility indicators ---
    indicators['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
    indicators['BB_upper'], indicators['BB_middle'], indicators['BB_lower'] = talib.BBANDS(
        df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
    )

    # --- Custom indicators ---
    indicators['SuperTrend'] = supertrend(df)

    return indicators
