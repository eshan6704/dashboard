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

def fetch_daily(symbol, date_end, date_start, b2_save=False):
    """
    Fetch daily historical stock data and generate full analysis dashboard with Plotly charts.
    """
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            print(f"[{date_end}] Using cached daily for {symbol}")
            return cached

    try:
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching daily for {symbol}")
        df = yf.download(symbol + ".NS", start=start, end=end)
        if df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")

        # Reset index and format Date
        df.reset_index(inplace=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")

        # Optional save to Backblaze
        if b2_save:
            b2.upload_file("eshanhf", f"daily/{symbol}.csv", df)

        # Calculate additional metrics
        df["Daily Return %"] = df["Close"].pct_change() * 100
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["UpperBB"] = df["Close"].rolling(20).mean() + 2*df["Close"].rolling(20).std()
        df["LowerBB"] = df["Close"].rolling(20).mean() - 2*df["Close"].rolling(20).std()

        # Summary stats
        summary = pd.DataFrame({
            "Metric": ["Start Date","End Date","Min Price","Max Price","Mean Price","Total Volume"],
            "Value": [df["Date"].iloc[0], df["Date"].iloc[-1],
                      format_large_number(df["Close"].min()),
                      format_large_number(df["Close"].max()),
                      format_large_number(df["Close"].mean()),
                      format_large_number(df["Volume"].sum())]
        })

        # Plotly figure
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1,
                            row_heights=[0.7,0.3],
                            specs=[[{"secondary_y": False}], [{"secondary_y": False}]])

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="OHLC"), row=1, col=1)

        # SMA/EMA overlays
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], mode="lines", name="SMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA50"], mode="lines", name="SMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["EMA20"], mode="lines", name="EMA20"), row=1, col=1)

        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df["Date"], y=df["UpperBB"], mode="lines", name="UpperBB", line=dict(dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["LowerBB"], mode="lines", name="LowerBB", line=dict(dash="dot")), row=1, col=1)

        # Volume bar chart
        fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume"), row=2, col=1)

        fig.update_layout(height=700, width=1000, title=f"{symbol} Daily Analysis",
                          xaxis_rangeslider_visible=False)

        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # Build table HTML
        table_html = wrap_html(f"<h2>Summary</h2>{summary.to_html(index=False, escape=False)}")
        data_table_html = wrap_html(f"<h2>OHLC Table</h2>{df.to_html(index=False, escape=False)}")

        # Combine full dashboard
        full_html = chart_html + table_html + data_table_html

        # Cache HTML
        persist.save(key, full_html, "html")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre>")
