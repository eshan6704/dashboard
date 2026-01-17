# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from . import persist
from . import chart_builder


def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"

    # -----------------------------
    # Cache HTML (UNCHANGED)
    # -----------------------------
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        # -----------------------------
        # Date conversion (UNCHANGED)
        # -----------------------------
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        # -----------------------------
        # Fetch data (UNCHANGED)
        # -----------------------------
        df = yf.download(symbol + ".NS", start=start, end=end)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return "<h3>No daily data found</h3>"

        # -----------------------------
        # Clean data (UNCHANGED)
        # -----------------------------
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # -----------------------------
        # Indicators (UNCHANGED)
        # -----------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # =================================================
        # CHARTS (NEW – but logic unchanged)
        # =================================================
        price_img = f"@stock@daily@{symbol}@price"
        ma_img    = f"@stock@daily@{symbol}@ma"

        if not persist.exists(price_img, "png"):
            img = chart_builder.build_price_volume(df, symbol)
            persist.save(price_img, img, "png", timestamped=False)

        if not persist.exists(ma_img, "png"):
            img = chart_builder.build_moving_avg(df, symbol)
            persist.save(ma_img, img, "png", timestamped=False)

        # =================================================
        # TABLE (UNCHANGED)
        # =================================================
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

        # =================================================
        # FINAL HTML (ONLY image src changed)
        # =================================================
        html = f"""
<div id="daily_dashboard">

<h2>{symbol} – Daily Analysis</h2>

<h3>Price Table (Last 100 Days)</h3>
<table border="1" cellpadding="6" width="100%">
<tr style="background:#f0f0f0;">
<th>Date</th>
<th>Open</th>
<th>High</th>
<th>Low</th>
<th>Close</th>
<th>Volume</th>
</tr>
{rows}
</table>

<h3>Price & Volume</h3>
<img src="@stock@daily@{symbol}@price.png" style="width:100%;max-width:1200px;">

<h3>Moving Averages</h3>
<img src="@stock@daily@{symbol}@ma.png" style="width:100%;max-width:1200px;">

</div>
"""

        persist.save(key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"