# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import traceback

from . import persist
from . import backblaze as b2
from .common import wrap_html, format_large_number

# ===========================================================
# RAW DAILY FETCHER (from your stock.py)
# ===========================================================
def daily(symbol, date_end, date_start):
    """Fetch daily OHLCV from Yahoo Finance."""
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    df = yf.download(symbol + ".NS", start=start, end=end).round(2)
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    return df

# ===========================================================
# DASHBOARD BUILDER
# ===========================================================
def fetch_daily(symbol, date_end, date_start, b2_save=False):
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            print(f"[{date_end}] Using cached daily for {symbol}")
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df is None or df.empty:
            return wrap_html(f'<div id="daily_wrapper"><h1>No daily data for {symbol}</h1></div>')

        # Reset index if not simple RangeIndex
        if not isinstance(df.index, pd.RangeIndex):
            df.reset_index(inplace=True)

        # Convert OHLCV to numeric safely
        numeric_cols = ["Open","High","Low","Close","Adj Close","Volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with missing essential data
        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index(drop=True)

        # Format date
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")

        if b2_save:
            b2.upload_file("eshanhf", f"daily/{symbol}.csv", df)

        # Indicators
        df["Daily Return %"] = df["Close"].pct_change()*100
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["UpperBB"] = df["Close"].rolling(20).mean() + 2*df["Close"].rolling(20).std()
        df["LowerBB"] = df["Close"].rolling(20).mean() - 2*df["Close"].rolling(20).std()
        df["ATR"] = df["High"].combine(df["Low"], lambda h,l: h-l).rolling(14).mean()

        # Summary stats
        summary = pd.DataFrame({
            "Metric": ["Start Date","End Date","Min Price","Max Price","Mean Price","Total Volume","Avg Daily Return %","Volatility ATR"],
            "Value": [
                df["Date"].iloc[0],
                df["Date"].iloc[-1],
                format_large_number(df["Close"].min()),
                format_large_number(df["Close"].max()),
                format_large_number(df["Close"].mean()),
                format_large_number(df["Volume"].sum()),
                f"{df['Daily Return %'].mean():.2f}%",
                f"{df['ATR'].mean():.2f}"
            ]
        })

        # Plotly dashboard
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.4,0.2,0.2,0.2],
                            specs=[[{}],[{}],[{}],[{}]])

        # Candlestick + moving averages + Bollinger
        fig.add_trace(go.Candlestick(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="OHLC"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA20"], mode="lines", name="EMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA50"], mode="lines", name="EMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["UpperBB"], mode="lines", name="UpperBB", line=dict(dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["LowerBB"], mode="lines", name="LowerBB", line=dict(dash="dot")), row=1, col=1)

        # Volume
        fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume"), row=2, col=1)
        # Daily Return %
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Daily Return %"], mode="lines+markers", name="Daily Return %"), row=3, col=1)
        # ATR
        fig.add_trace(go.Scatter(x=df["Date"], y=df["ATR"], mode="lines", name="ATR"), row=4, col=1)

        fig.update_layout(height=1000, width=1200, title=f"{symbol} Daily Analysis Dashboard", xaxis_rangeslider_visible=False)

        chart_html = ""
        try:
            chart_html = f'<div id="chart_dashboard">{fig.to_html(full_html=False, include_plotlyjs="cdn")}</div>'
        except Exception as e:
            chart_html = f'<div id="chart_dashboard"><h2>Chart generation failed: {e}</h2></div>'

        # Tables wrapped in divs
        table_html = f'<div id="summary_stats"><h2>Summary Stats</h2>{summary.to_html(index=False, escape=False)}</div>'
        data_table_html = f'<div id="ohlc_table"><h2>OHLC Table</h2>{df.to_html(index=False, escape=False)}</div>'

        full_html = chart_html + table_html + data_table_html

        persist.save(key, full_html, "html")
        return full_html

    except Exception as e:
        return wrap_html(f'<div id="daily_wrapper"><h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre></div>')
