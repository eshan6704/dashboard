# indicators.py
import pandas as pd
import numpy as np

# Try TA-Lib
try:
    import talib
    TALIB = True
except:
    TALIB = False


# ============================================================
# BASIC INDICATORS (SMA, EMA, ATR)
# ============================================================

def sma(series, period):
    return series.rolling(period).mean()


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def atr(high, low, close, period=14):
    if TALIB and hasattr(talib, "ATR"):
        return talib.ATR(high, low, close, timeperiod=period)
    else:
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean()


# ============================================================
# SUPERTREND — TradingView Perfect Replication
# ============================================================

def supertrend(df, period=10, multiplier=3):
    """
    Returns:
    ST: SuperTrend line
    DIR: Trend direction (True = Uptrend, False = Downtrend)
    """
    high = df['High']
    low = df['Low']
    close = df['Close']

    # ATR
    atr_val = atr(high, low, close, period)

    # Basic bands
    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr_val
    lowerband = hl2 - multiplier * atr_val

    final_upper = upperband.copy()
    final_lower = lowerband.copy()

    for i in range(1, len(df)):
        # Final upper band
        if upperband.iloc[i] < final_upper.iloc[i - 1] or close.iloc[i - 1] > final_upper.iloc[i - 1]:
            final_upper.iloc[i] = upperband.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        # Final lower band
        if lowerband.iloc[i] > final_lower.iloc[i - 1] or close.iloc[i - 1] < final_lower.iloc[i - 1]:
            final_lower.iloc[i] = lowerband.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

    # Supertrend
    st = pd.Series(index=df.index)
    dir_up = pd.Series(index=df.index, dtype=bool)

    for i in range(1, len(df)):
        if close.iloc[i] > final_upper.iloc[i - 1]:
            dir_up.iloc[i] = True
        elif close.iloc[i] < final_lower.iloc[i - 1]:
            dir_up.iloc[i] = False
        else:
            dir_up.iloc[i] = dir_up.iloc[i - 1]

        st.iloc[i] = final_lower.iloc[i] if dir_up.iloc[i] else final_upper.iloc[i]

    return st, dir_up


# ============================================================
# KELTNER CHANNEL — (EMA ± ATR * Mult)
# ============================================================

def keltner_channel(df, ema_period=20, atr_period=10, mult=2):
    close = df['Close']
    upper = ema(close, ema_period) + mult * atr(df['High'], df['Low'], df['Close'], atr_period)
    lower = ema(close, ema_period) - mult * atr(df['High'], df['Low'], df['Close'], atr_period)
    mid = ema(close, ema_period)
    return mid, upper, lower


# ============================================================
# ZIGZAG — PERCENT BASED
# ============================================================

def zigzag(series, pct=5):
    """
    Returns ZigZag turning points based on percentage move.
    """
    zz = pd.Series(index=series.index, dtype=float)
    last_pivot_price = series.iloc[0]
    last_pivot_idx = series.index[0]
    trend = 0  # +1 up, -1 down

    for i in range(1, len(series)):
        change = (series.iloc[i] - last_pivot_price) / last_pivot_price * 100

        if trend >= 0 and change <= -pct:
            zz.iloc[i] = series.iloc[i]
            last_pivot_price = series.iloc[i]
            trend = -1

        elif trend <= 0 and change >= pct:
            zz.iloc[i] = series.iloc[i]
            last_pivot_price = series.iloc[i]
            trend = +1

    return zz


# ============================================================
# SWING HIGH / SWING LOW
# ============================================================

def swing_high_low(df, window=5):
    """
    Identifies swing high/low using window method.
    For window=5, center index is 2 (2 left, 2 right)
    """
    highs = df['High']
    lows = df['Low']
    idx = df.index

    swing_high = pd.Series(np.nan, index=idx)
    swing_low = pd.Series(np.nan, index=idx)

    half = window // 2

    for i in range(half, len(df) - half):
        segment_high = highs[i - half: i + half + 1]
        segment_low = lows[i - half: i + half + 1]

        if highs.iloc[i] == segment_high.max():
            swing_high.iloc[i] = highs.iloc[i]

        if lows.iloc[i] == segment_low.min():
            swing_low.iloc[i] = lows.iloc[i]

    return swing_high, swing_low


# ============================================================
# RSI FALLBACK
# ============================================================

def rsi(series, period=14):
    if TALIB and hasattr(talib, "RSI"):
        return talib.RSI(series, timeperiod=period)
    else:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ema_up = up.ewm(span=period).mean()
        ema_down = down.ewm(span=period).mean()
        rs = ema_up / ema_down
        return 100 - (100 / (1 + rs))


# ============================================================
# MACD FALLBACK
# ============================================================

def macd(series, fast=12, slow=26, signal=9):
    if TALIB and hasattr(talib, "MACD"):
        macd_line, macd_signal, macd_hist = talib.MACD(series, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return macd_line, macd_signal, macd_hist
    else:
        ema_fast = ema(series, fast)
        ema_slow = ema(series, slow)
        macd_line = ema_fast - ema_slow
        macd_signal = ema(macd_line, signal)
        macd_hist = macd_line - macd_signal
        return macd_line, macd_signal, macd_hist


# ============================================================
# STOCHASTIC FALLBACK
# ============================================================

def stochastic(df, k_period=14, d_period=3):
    if TALIB and hasattr(talib, "STOCH"):
        k, d = talib.STOCH(
            df['High'], df['Low'], df['Close'],
            fastk_period=k_period,
            slowk_period=d_period, slowk_matype=0,
            slowd_period=d_period, slowd_matype=0
        )
        return k, d
    else:
        low_min = df['Low'].rolling(k_period).min()
        high_max = df['High'].rolling(k_period).max()
        k = (df['Close'] - low_min) * 100 / (high_max - low_min)
        d = k.rolling(d_period).mean()
        return k, d
