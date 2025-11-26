# daily.py
import yfinance as yf
import pandas as pd
import talib
import numpy as np
import plotly.graph_objs as go

STYLE_BLOCK = """
<style>
.styled-table { border-collapse: collapse; margin: 10px 0; font-size: 0.9em; font-family: sans-serif; width: 100%; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
.styled-table th, .styled-table td { padding: 8px 10px; border: 1px solid #ddd;}
.styled-table tbody tr:nth-child(even) { background-color: #f9f9f9;}
.button { margin:5px; padding:5px 10px; border-radius:5px; border:1px solid #0077cc; background:#0077cc; color:#fff; cursor:pointer;}
.button:hover { background:#005fa3; }
</style>
"""

# --- Custom functions ---
def supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    tr = pd.concat([df['High'] - df['Low'],
                    abs(df['High'] - df['Close'].shift()),
                    abs(df['Low'] - df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr
    st = pd.Series(index=df.index)
    trend_up = True
    for i in range(1, len(df)):
        if df['Close'][i] > upperband[i-1]:
            trend_up = True
        elif df['Close'][i] < lowerband[i-1]:
            trend_up = False
        st[i] = lowerband[i] if trend_up else upperband[i]
    return st

def zigzag(df, pct=5):
    zz = pd.Series(index=df.index)
    last_pivot = df['Close'][0]
    trend = 0
    for i in range(1, len(df)):
        change = (df['Close'][i] - last_pivot) / last_pivot * 100
        if trend >= 0 and change <= -pct:
            zz[i] = df['Close'][i]
            last_pivot = df['Close'][i]
            trend = -1
        elif trend <= 0 and change >= pct:
            zz[i] = df['Close'][i]
            last_pivot = df['Close'][i]
            trend = 1
    return zz

def swing_high_low(df, window=5):
    df['SwingHigh'] = df['High'].rolling(window, center=True).max()
    df['SwingLow'] = df['Low'].rolling(window, center=True).min()
    return df

def keltner_channel(df, period=20, atr_mult=2):
    ema = talib.EMA(df['Close'], period)
    tr = pd.concat([df['High'] - df['Low'],
                    abs(df['High'] - df['Close'].shift()),
                    abs(df['Low'] - df['Close'].shift())], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    df['KC_Upper'] = ema + atr_mult * atr
    df['KC_Lower'] = ema - atr_mult * atr
    return df

# --- Main function ---
def fetch_daily(symbol):
    yfsymbol = symbol + ".NS"
    content_html = f"<h1>No daily data for {symbol}</h1>"

    try:
        df = yf.download(yfsymbol, period="1y", interval="1d").round(2)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # --- TA-Lib indicators ---
            df["SMA20"] = talib.SMA(df["Close"], timeperiod=20)
            df["SMA50"] = talib.SMA(df["Close"], timeperiod=50)
            df["EMA20"] = talib.EMA(df["Close"], timeperiod=20)
            df["RSI14"] = talib.RSI(df["Close"], timeperiod=14)
            df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

            # --- Custom indicators ---
            df["SuperTrend"] = supertrend(df)
            df = keltner_channel(df)
            df["ZigZag"] = zigzag(df)
            df = swing_high_low(df)

            # --- Plotly chart ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="Price"
            ))

            # Indicators toggle
            indicators = ["SMA20","SMA50","EMA20","RSI14","MACD","MACD_Signal",
                          "SuperTrend","KC_Upper","KC_Lower","ZigZag","SwingHigh","SwingLow"]

            for ind in indicators:
                yaxis = 'y2' if ind in ["RSI14","MACD","MACD_Signal"] else 'y'
                fig.add_trace(go.Scatter(x=df.index, y=df[ind], mode='lines+markers' if 'Swing' in ind or 'ZigZag' in ind else 'lines',
                                         name=ind, visible=False, yaxis=yaxis))

            buttons=[]
            for i, ind in enumerate(indicators):
                visible=[True]+[False]*len(indicators)
                visible[i+1]=True
                buttons.append(dict(label=ind, method="restyle", args=[{"visible":visible}]))
            buttons.append(dict(label="All Off", method="restyle", args=[{"visible":[True]+[False]*len(indicators)}]))

            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price",
                yaxis2=dict(title="Indicator", overlaying="y", side="right"),
                xaxis_rangeslider_visible=False,
                height=700,
                updatemenus=[dict(type="buttons", x=1.05, y=0.8, buttons=buttons)]
            )

            chart_html = fig.to_html(full_html=False)
            table_html = df.tail(30).to_html(classes="styled-table", border=0)
            content_html = f"{chart_html}<h2>Recent Daily Data (last 30 rows)</h2>{table_html}"

    except Exception as e:
        content_html = f"<h1>Error</h1><p>{e}</p>"

    return f"<!DOCTYPE html><html><head>{STYLE_BLOCK}</head><body>{content_html}</body></html>"
