# indicator.py
import pandas as pd
import numpy as np

# Try TA-Lib
try:
    import talib
    TALIB_AVAILABLE = True
except:
    TALIB_AVAILABLE = False


# ==============================
# MACD
# ==============================
def calc_macd(df):
    if TALIB_AVAILABLE:
        macd, signal, hist = talib.MACD(df["Close"])
    else:
        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        hist = macd - signal

    return pd.DataFrame({
        "MACD": macd,
        "Signal": signal,
        "Histogram": hist
    })


# ==============================
# RSI
# ==============================
def calc_rsi(df):
    if TALIB_AVAILABLE:
        rsi = talib.RSI(df["Close"], timeperiod=14)
    else:
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

    return pd.DataFrame({"RSI": rsi})


# ==============================
# Supertrend (Custom)
# ==============================
def calc_supertrend(df, period=10, multiplier=3):
    hl2 = (df["High"] + df["Low"]) / 2
    tr1 = df["High"] - df["Low"]
    tr2 = abs(df["High"] - df["Close"].shift())
    tr3 = abs(df["Low"] - df["Close"].shift())
    tr = tr1.combine(tr2, max).combine(tr3, max)

    atr = tr.rolling(period).mean()
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    for i in range(len(df)):
        if i == 0:
            st.iloc[i] = upperband.iloc[i]
            direction.iloc[i] = 1
        else:
            if df["Close"].iloc[i] > st.iloc[i - 1]:
                st.iloc[i] = lowerband.iloc[i]
                direction.iloc[i] = 1
            else:
                st.iloc[i] = upperband.iloc[i]
                direction.iloc[i] = -1

    return pd.DataFrame({
        "Supertrend": st,
        "Direction": direction
    })


# ==============================
# Stochastic
# ==============================
def calc_stochastic(df):
    if TALIB_AVAILABLE:
        slowk, slowd = talib.STOCH(df["High"], df["Low"], df["Close"])
    else:
        low14 = df["Low"].rolling(14).min()
        high14 = df["High"].rolling(14).max()
        slowk = (df["Close"] - low14) * 100 / (high14 - low14)
        slowd = slowk.rolling(3).mean()

    return pd.DataFrame({"STOCH_K": slowk, "STOCH_D": slowd})


# ==============================
# Keltner Channel
# ==============================
def calc_keltner(df):
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    ema = typical.ewm(span=20).mean()
    atr = (df["High"] - df["Low"]).rolling(20).mean()

    upper = ema + 2 * atr
    lower = ema - 2 * atr

    return pd.DataFrame({"KC_UP": upper, "KC_MID": ema, "KC_LOW": lower})


# ==============================
# ZigZag (simplified)
# ==============================
def calc_zigzag(df, pct=3):
    zigzag = [np.nan] * len(df)
    last_pivot = df["Close"].iloc[0]

    for i in range(1, len(df)):
        change = (df["Close"].iloc[i] - last_pivot) / last_pivot * 100
        if abs(change) >= pct:
            zigzag[i] = df["Close"].iloc[i]
            last_pivot = df["Close"].iloc[i]

    return pd.DataFrame({"ZIGZAG": zigzag})


# ==============================
# Swing High / Low
# ==============================
def calc_swings(df, period=5):
    swing_high = df["High"].rolling(period).max()
    swing_low = df["Low"].rolling(period).min()

    return pd.DataFrame({
        "SWING_HIGH": swing_high,
        "SWING_LOW": swing_low
    })
