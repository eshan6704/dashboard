# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback
from . import persist
from . import chart_builder

def fetch_daily(symbol, date_end, date_start):
    """
    Generates HTML for daily stock analysis with embedded charts.
    Returns HTML as string.
    """
    key_html = f"@stock@daily@{symbol}.html"

    # Check cached HTML
    if persist.exists(key_html, "html"):
        return persist.load(key_html, "html")

    try:
        # Parse dates
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        # Fetch data
        df = yf.download(symbol + ".NS", start=start, end=end)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            return "<h3>No daily data found</h3>"

        # Clean data
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # Indicators
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # Generate charts
        price_name, price_bytes = chart_builder.price_volume(df, symbol)
        ma_name, ma_bytes = chart_builder.moving_avg(df, symbol)

        # Save charts
        persist.save(price_name, price_bytes, "jpeg", timestamped=False)
        persist.save(ma_name, ma_bytes, "jpeg", timestamped=False)

        # Generate table HTML
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

        # Build final HTML
        html = f"""
<div id="daily_dashboard">
<h2>{symbol} – Daily Analysis</h2>

<h3>Price Table (Last 100 Days)</h3>
<table style="border-collapse:collapse;width:100%;" border="1" cellpadding="6">
<tr style="background:#f0f0f0;font-weight:bold;">
    <th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>
</tr>
{rows}
</table>

<h3>Price & Volume</h3>
<img src="{price_name}" style="width:100%;max-width:1200px;">

<h3>Moving Averages</h3>
<img src="{ma_name}" style="width:100%;max-width:1200px;">
</div>
"""
        # Save HTML
        persist.save(key_html, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"