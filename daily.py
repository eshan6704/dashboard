# daily.py
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Try to import TA-Lib; if unavailable, will use fallback implementations
try:
    import talib
    TALIB_AVAILABLE = True
except Exception:
    TALIB_AVAILABLE = False

from common import wrap_html, STYLE_BLOCK

# --- Helper fallback implementations (used if TA-Lib isn't available) ---
def sma_fallback(series, period):
    return series.rolling(period).mean()

def ema_fallback(series, period):
    return series.ewm(span=period, adjust=False).mean()

def macd_fallback(close, fast=12, slow=26, signal=9):
    fast_ema = ema_fallback(close, fast)
    slow_ema = ema_fallback(close, slow)
    macd = fast_ema - slow_ema
    macd_signal = ema_fallback(macd, signal)
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

def atr_fallback(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr

def stoch_fallback(high, low, close, k_period=14, d_period=3):
    low_min = low.rolling(k_period).min()
    high_max = high.rolling(k_period).max()
    k = 100 * (close - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d

# SuperTrend (custom)
def supertrend_fallback(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = atr_fallback(df['High'], df['Low'], df['Close'], period=period)
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index, dtype=float)
    trend = pd.Series(index=df.index, dtype=bool)  # True = uptrend, False = downtrend

    # initialize
    st.iloc[0] = np.nan
    trend.iloc[0] = True

    for i in range(1, len(df)):
        if df['Close'].iat[i] > upperband.iat[i-1]:
            trend.iat[i] = True
        elif df['Close'].iat[i] < lowerband.iat[i-1]:
            trend.iat[i] = False
        else:
            trend.iat[i] = trend.iat[i-1]
            if trend.iat[i] and lowerband.iat[i] < st.iat[i-1]:
                lowerband.iat[i] = st.iat[i-1]
            if not trend.iat[i] and upperband.iat[i] > st.iat[i-1]:
                upperband.iat[i] = st.iat[i-1]

        st.iat[i] = lowerband.iat[i] if trend.iat[i] else upperband.iat[i]

    return st, trend

# ZigZag (simple percent threshold)
def zigzag_fallback(close_series, pct=5.0):
    zz = pd.Series(index=close_series.index, dtype=float)
    last_extreme_idx = 0
    last_extreme_price = close_series.iat[0]
    last_trend = 0  # 1 = up, -1 = down, 0 = unknown
    for i in range(1, len(close_series)):
        change = (close_series.iat[i] - last_extreme_price) / last_extreme_price * 100.0
        if last_trend >= 0 and change <= -pct:
            zz.iat[i] = close_series.iat[i]
            last_extreme_idx = i
            last_extreme_price = close_series.iat[i]
            last_trend = -1
        elif last_trend <= 0 and change >= pct:
            zz.iat[i] = close_series.iat[i]
            last_extreme_idx = i
            last_extreme_price = close_series.iat[i]
            last_trend = 1
    return zz

# Swing High/Low via rolling window
def swing_high_low(df, window=5):
    df = df.copy()
    df['SwingHigh'] = df['High'].rolling(window, center=True).max()
    df['SwingLow'] = df['Low'].rolling(window, center=True).min()
    # Only keep values where the center equals the extreme (to mark pivot)
    center = window // 2
    swing_high = [np.nan]*len(df)
    swing_low = [np.nan]*len(df)
    highs = df['High'].values
    lows = df['Low'].values
    for i in range(center, len(df)-center):
        window_high = highs[i-center:i+center+1]
        window_low = lows[i-center:i+center+1]
        if highs[i] == np.max(window_high):
            swing_high[i] = highs[i]
        if lows[i] == np.min(window_low):
            swing_low[i] = lows[i]
    df['SwingHigh'] = swing_high
    df['SwingLow'] = swing_low
    return df['SwingHigh'], df['SwingLow']

# Keltner Channel (EMA ± ATR * mult)
def keltner_channel(df, ema_period=20, atr_period=10, atr_mult=2):
    if TALIB_AVAILABLE:
        ema = talib.EMA(df['Close'], timeperiod=ema_period)
        atr = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=atr_period)
    else:
        ema = ema_fallback(df['Close'], ema_period)
        atr = atr_fallback(df['High'], df['Low'], df['Close'], period=atr_period)
    upper = ema + atr_mult * atr
    lower = ema - atr_mult * atr
    return upper, lower

# --- Main fetch function ---
def fetch_daily(symbol,
                period="1y",
                interval="1d",
                supertrend_period=10,
                supertrend_mult=3,
                keltner_ema=20,
                keltner_atr=10,
                keltner_mult=2,
                zigzag_pct=5.0):
    """
    Returns full HTML with multi-panel Plotly chart (price, volume, MACD, Stochastic)
    and controls (buttons) to toggle indicators.
    """
    yfsymbol = f"{symbol}.NS"
    try:
        df = yf.download(yfsymbol, period=period, interval=interval).round(6)
    except Exception as e:
        return wrap_html("Error", f"<h1>Error fetching data for {symbol}</h1><p>{str(e)}</p>")

    if df is None or df.empty:
        return wrap_html("No Data", f"<h1>No {interval} data for {symbol} (period={period})</h1>")

    # Ensure datetime index is proper
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Compute indicators (TA-Lib if available, else fallback)
    if TALIB_AVAILABLE:
        # moving averages
        df['SMA20'] = talib.SMA(df['Close'], timeperiod=20)
        df['SMA50'] = talib.SMA(df['Close'], timeperiod=50)
        df['EMA20'] = talib.EMA(df['Close'], timeperiod=20)
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = macd, macd_signal, macd_hist
        # Stochastic
        slowk, slowd = talib.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df['StochK'], df['StochD'] = slowk, slowd
        # ATR for SuperTrend/Keltner
        df['ATR14'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
    else:
        # SMA/EMA fallback
        df['SMA20'] = sma_fallback(df['Close'], 20)
        df['SMA50'] = sma_fallback(df['Close'], 50)
        df['EMA20'] = ema_fallback(df['Close'], 20)
        # MACD fallback
        macd, macd_signal, macd_hist = macd_fallback(df['Close'], 12, 26, 9)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = macd, macd_signal, macd_hist
        # Stoch fallback
        stoch_k, stoch_d = stoch_fallback(df['High'], df['Low'], df['Close'], 14, 3)
        df['StochK'], df['StochD'] = stoch_k, stoch_d
        df['ATR14'] = atr_fallback(df['High'], df['Low'], df['Close'], period=14)

    # SuperTrend (custom using ATR)
    try:
        st_values, st_trend = supertrend_fallback(df, period=supertrend_period, multiplier=supertrend_mult)
        df['SuperTrend'] = st_values
        df['SuperTrendDir'] = st_trend
    except Exception:
        # if fails, fill NaN
        df['SuperTrend'] = np.nan
        df['SuperTrendDir'] = np.nan

    # Keltner Channel
    try:
        kc_upper, kc_lower = keltner_channel(df, ema_period=keltner_ema, atr_period=keltner_atr, atr_mult=keltner_mult)
        df['KC_Upper'] = kc_upper
        df['KC_Lower'] = kc_lower
    except Exception:
        df['KC_Upper'] = np.nan
        df['KC_Lower'] = np.nan

    # ZigZag
    try:
        df['ZigZag'] = zigzag_fallback(df['Close'], pct=zigzag_pct)
    except Exception:
        df['ZigZag'] = np.nan

    # Swing High/Low
    try:
        sh, sl = swing_high_low(df, window=5)
        df['SwingHigh'] = sh
        df['SwingLow'] = sl
    except Exception:
        df['SwingHigh'] = np.nan
        df['SwingLow'] = np.nan

    # OBV or Volume smoothing if needed (not required but left as data)
    df['VolumeSmoothed'] = df['Volume'].rolling(3).mean()

    # Build Plotly subplots: 4 rows (price, volume, MACD, Stochastic)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.12, 0.18, 0.18],
                        specs=[[{"secondary_y": False}],
                               [{"secondary_y": False}],
                               [{"secondary_y": False}],
                               [{"secondary_y": False}]])

    x = df.index

    # Row 1: Candlestick
    fig.add_trace(go.Candlestick(x=x, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                 name='Price', increasing_line_color='green', decreasing_line_color='red'), row=1, col=1)

    # SuperTrend (line, colored by trend)
    fig.add_trace(go.Scatter(x=x, y=df['SuperTrend'], mode='lines', name='SuperTrend', visible=True,
                             line=dict(width=2, dash='dash')), row=1, col=1)

    # SMA & EMA
    fig.add_trace(go.Scatter(x=x, y=df['SMA20'], mode='lines', name='SMA20', visible=True, line=dict(width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['SMA50'], mode='lines', name='SMA50', visible=False, line=dict(width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['EMA20'], mode='lines', name='EMA20', visible=False, line=dict(width=1, dash='dot')), row=1, col=1)

    # Keltner Channels
    fig.add_trace(go.Scatter(x=x, y=df['KC_Upper'], mode='lines', name='KC Upper', visible=False, line=dict(width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['KC_Lower'], mode='lines', name='KC Lower', visible=False, line=dict(width=1)), row=1, col=1)

    # ZigZag and Swing markers as markers on price panel
    fig.add_trace(go.Scatter(x=x, y=df['ZigZag'], mode='markers', name='ZigZag', visible=False,
                             marker=dict(symbol='diamond', size=8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['SwingHigh'], mode='markers', name='Swing High', visible=False,
                             marker=dict(symbol='triangle-up', size=8, color='purple')), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['SwingLow'], mode='markers', name='Swing Low', visible=False,
                             marker=dict(symbol='triangle-down', size=8, color='brown')), row=1, col=1)

    # Row 2: Volume
    fig.add_trace(go.Bar(x=x, y=df['Volume'], name='Volume', marker_color='lightblue', visible=True), row=2, col=1)

    # Row 3: MACD (line + signal + histogram as bar)
    fig.add_trace(go.Scatter(x=x, y=df['MACD'], mode='lines', name='MACD', visible=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['MACD_Signal'], mode='lines', name='MACD Signal', visible=False), row=3, col=1)
    fig.add_trace(go.Bar(x=x, y=df['MACD_Hist'], name='MACD Hist', visible=False), row=3, col=1)

    # Row 4: Stochastic (%K & %D)
    fig.add_trace(go.Scatter(x=x, y=df['StochK'], mode='lines', name='Stoch %K', visible=False), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=df['StochD'], mode='lines', name='Stoch %D', visible=False), row=4, col=1)

    # Layout defaults
    fig.update_layout(
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        height=1000,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    # Prepare updatemenu buttons for toggling indicators
    # Determine trace indices in the order they were added:
    # 0 price candlestick
    # 1 supertrend
    # 2 SMA20
    # 3 SMA50
    # 4 EMA20
    # 5 KC Upper
    # 6 KC Lower
    # 7 ZigZag
    # 8 SwingHigh
    # 9 SwingLow
    # 10 Volume
    # 11 MACD
    # 12 MACD Signal
    # 13 MACD Hist
    # 14 StochK
    # 15 StochD

    total_traces = len(fig.data)  # should be 16

    # Helper to create visible array with selective traces visible
    def visible_array(show_indices):
        arr = [False] * total_traces
        # keep price and volume visible by default in any selection for context
        arr[0] = True   # candle
        arr[10] = True  # volume (index may vary—check length; we've added bar at position 10)
        for i in show_indices:
            if 0 <= i < total_traces:
                arr[i] = True
        return arr

    # Map indicator buttons to the trace indices they affect
    buttons = []

    # SuperTrend
    buttons.append(dict(label="SuperTrend",
                        method="restyle",
                        args=[{"visible": visible_array([1])}]))

    # SMA20
    buttons.append(dict(label="SMA20",
                        method="restyle",
                        args=[{"visible": visible_array([2])}]))

    # SMA50
    buttons.append(dict(label="SMA50",
                        method="restyle",
                        args=[{"visible": visible_array([3])}]))

    # EMA20
    buttons.append(dict(label="EMA20",
                        method="restyle",
                        args=[{"visible": visible_array([4])}]))

    # Keltner Channel
    buttons.append(dict(label="Keltner",
                        method="restyle",
                        args=[{"visible": visible_array([5,6])}]))

    # ZigZag
    buttons.append(dict(label="ZigZag",
                        method="restyle",
                        args=[{"visible": visible_array([7])}]))

    # Swing HI/LO
    buttons.append(dict(label="Swing H/L",
                        method="restyle",
                        args=[{"visible": visible_array([8,9])}]))

    # MACD
    buttons.append(dict(label="MACD",
                        method="restyle",
                        args=[{"visible": visible_array([11,12,13])}]))

    # Stochastic
    buttons.append(dict(label="Stochastic",
                        method="restyle",
                        args=[{"visible": visible_array([14,15])}]))

    # Show All (turn on all traces)
    buttons.append(dict(label="All On",
                        method="restyle",
                        args=[{"visible": [True]*total_traces}]))

    # All Off (only show price and volume)
    buttons.append(dict(label="All Off",
                        method="restyle",
                        args=[{"visible": visible_array([])}]))

    # Reset (default view: price, volume, supertrend, SMA20)
    buttons.append(dict(label="Reset",
                        method="restyle",
                        args=[{"visible": visible_array([1,2])}]))

    fig.update_layout(
        updatemenus=[dict(type="buttons", direction="down", buttons=buttons, x=1.02, xanchor="left", y=0.95, yanchor="top")]
    )

    # Finalize: add a table (recent 30 rows) below chart area as HTML
    table_html = df.tail(30)[['Open', 'High', 'Low', 'Close', 'Volume']].round(2).to_html(classes="styled-table", border=0)

    chart_div = fig.to_html(full_html=False, include_plotlyjs='cdn')

    content_html = f"""
    <div class='card'>
        <h2>Daily Chart - {symbol.upper()}</h2>
        <div class='card-content-grid'>
            <div style="width:100%">{chart_div}</div>
        </div>
    </div>
    <div class='big-box'>
        <h2>Recent Daily Data (last 30 rows)</h2>
        {table_html}
    </div>
    """

    return wrap_html(f"Daily Chart for {symbol}", content_html, style_block=STYLE_BLOCK)
