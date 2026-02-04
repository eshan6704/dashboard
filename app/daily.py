# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from .svg_charts import candlestick_with_volume


def fetch_daily(symbol, date_end, date_start):
    try:
        # -------------------------------------------------
        # Date conversion
        # -------------------------------------------------
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        # -------------------------------------------------
        # Fetch data
        # -------------------------------------------------
        df = yf.download(symbol + ".NS", start=start, end=end)

        if df.empty:
            return "<h3>No daily data found</h3>"

        # 🔑 CRITICAL: flatten MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # -------------------------------------------------
        # Clean & normalize
        # -------------------------------------------------
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # -------------------------------------------------
        # Indicators
        # -------------------------------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # -------------------------------------------------
        # Views
        # -------------------------------------------------
        view_120 = df.tail(120)
        view_30  = df.tail(30)

        # -------------------------------------------------
        # SVG charts (INLINE)
        # -------------------------------------------------
        chart_main = candlestick_with_volume(
            view_120,
            title=f"{symbol} – Daily Candlestick (120 days)"
        )

        chart_short = candlestick_with_volume(
            view_30,
            title=f"{symbol} – Short Term (30 days)"
        )

        # -------------------------------------------------
        # Table (last 100 rows)
        # -------------------------------------------------
        rows = ""
        for r in view_120.tail(100).itertuples():
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

        # -------------------------------------------------
        # Final HTML (single payload)
        # -------------------------------------------------
        html = f"""
<div style="font-family:Arial;background:white;color:#111;padding:10px">

<h2>{symbol} – Daily Stock Dashboard</h2>

<h3>Main Trend</h3>
{chart_main}

<h3>Short-Term Trend</h3>
{chart_short}

<h3>Historical Data (Last 100 Days)</h3>
<table border="1" cellpadding="6" width="100%"
       style="border-collapse:collapse;font-size:13px">
<tr style="background:#f2f2f2">
<th>Date</th>
<th>Open</th>
<th>High</th>
<th>Low</th>
<th>Close</th>
<th>Volume</th>
</tr>
{rows}
</table>

</div>
"""

        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
