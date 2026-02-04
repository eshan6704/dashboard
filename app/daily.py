# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from .svg_charts import candlestick_with_volume


def fetch_daily(symbol, date_end, date_start):
    try:
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        df = yf.download(symbol + ".NS", start=start, end=end)

        if df.empty:
            return "<h3>No data</h3>"

        df = df.reset_index()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c])

        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        view = df.tail(120)

        # ---- MULTIPLE CHARTS ----
        chart_main = candlestick_with_volume(
            view, f"{symbol} Daily Candlestick"
        )

        chart_short = candlestick_with_volume(
            view.tail(30), f"{symbol} Last 30 Days"
        )

        # ---- Table ----
        rows = ""
        for r in view.itertuples():
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

        return f"""
<div style="font-family:Arial;background:white;color:#111">

<h2>{symbol} – Daily Dashboard</h2>

<h3>Primary Trend</h3>
{chart_main}

<h3>Short-Term View</h3>
{chart_short}

<h3>Historical Data</h3>
<table border="1" cellpadding="6" width="100%"
       style="border-collapse:collapse">
<tr style="background:#f5f5f5">
<th>Date</th><th>Open</th><th>High</th>
<th>Low</th><th>Close</th><th>Volume</th>
</tr>
{rows}
</table>

</div>
"""

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
