# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback
import os
import plotly.graph_objects as go
from . import persist

BASE_STATIC = "/app/app/static/charts/daily"

# ============================================================
def daily(symbol, date_end, date_start):
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

    df = yf.download(symbol + ".NS", start=start, end=end)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "Date"
    return df


# ============================================================
def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df.empty:
            return "<h1>No data</h1>"

        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # ------------------------------------------------
        # IMAGE PATHS
        # ------------------------------------------------
        sym_dir = f"{BASE_STATIC}/{symbol}"
        os.makedirs(sym_dir, exist_ok=True)

        candle_path = f"{sym_dir}/candle.png"
        ma_path = f"{sym_dir}/ma.png"

        candle_url = f"/static/charts/daily/{symbol}/candle.png"
        ma_url = f"/static/charts/daily/{symbol}/ma.png"

        # ------------------------------------------------
        # CANDLESTICK IMAGE
        # ------------------------------------------------
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df["DateStr"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"]
        ))

        fig.add_trace(go.Bar(
            x=df["DateStr"],
            y=df["Volume"],
            yaxis="y2",
            opacity=0.3
        ))

        fig.update_layout(
            height=600,
            yaxis=dict(title="Price"),
            yaxis2=dict(overlaying="y", side="right", title="Volume"),
            xaxis_rangeslider_visible=False
        )

        fig.write_image(candle_path, scale=2)

        # ------------------------------------------------
        # MA IMAGE
        # ------------------------------------------------
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["DateStr"], y=df["Close"], name="Close"))
        fig2.add_trace(go.Scatter(x=df["DateStr"], y=df["MA20"], name="MA20"))
        fig2.add_trace(go.Scatter(x=df["DateStr"], y=df["MA50"], name="MA50"))

        fig2.update_layout(height=500)
        fig2.write_image(ma_path, scale=2)

        # ------------------------------------------------
        # TABLE HTML
        # ------------------------------------------------
        rows = ""
        for r in df.tail(100).itertuples():
            rows += f"""
            <tr>
                <td>{r.DateStr}</td>
                <td>{r.Open:.2f}</td>
                <td>{r.High:.2f}</td>
                <td>{r.Low:.2f}</td>
                <td>{r.Close:.2f}</td>
                <td>{int(r.Volume)}</td>
            </tr>
            """

        html = f"""
<h2>{symbol} Daily Dashboard</h2>

<h3>Price Table</h3>
<table border="1" cellpadding="4">
<tr>
<th>Date</th><th>Open</th><th>High</th>
<th>Low</th><th>Close</th><th>Volume</th>
</tr>
{rows}
</table>

<h3>Candlestick Chart</h3>
<img src="{candle_url}" style="width:100%;max-width:1200px;">

<h3>Moving Averages</h3>
<img src="{ma_url}" style="width:100%;max-width:1200px;">
"""

        persist.save(key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
