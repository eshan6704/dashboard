# daily.py

import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
import os
import traceback
from . import persist

# ============================================================
# Static path (HF serves this automatically)
# ============================================================
BASE_STATIC = "/app/app/static/charts/daily"


# ============================================================
def fetch_daily(symbol, date_end, date_start):
    """
    Fetch daily OHLCV data from Yahoo Finance,
    generate PNG charts using matplotlib,
    and return FULL HTML to frontend.
    """

    cache_key = f"daily_{symbol}"

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------
    if persist.exists(cache_key, "html"):
        cached = persist.load(cache_key, "html")
        if cached:
            return cached

    try:
        # ----------------------------------------------------
        # Date handling
        # ----------------------------------------------------
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        # ----------------------------------------------------
        # Fetch data
        # ----------------------------------------------------
        df = yf.download(symbol + ".NS", start=start, end=end)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return "<h2>No data available</h2>"

        # ----------------------------------------------------
        # Clean & prepare
        # ----------------------------------------------------
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # ----------------------------------------------------
        # Indicators
        # ----------------------------------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # ----------------------------------------------------
        # Output paths
        # ----------------------------------------------------
        out_dir = f"{BASE_STATIC}/{symbol}"
        os.makedirs(out_dir, exist_ok=True)

        price_png = f"{out_dir}/price_volume.png"
        ma_png    = f"{out_dir}/moving_avg.png"

        price_url = f"/static/charts/daily/{symbol}/price_volume.png"
        ma_url    = f"/static/charts/daily/{symbol}/moving_avg.png"

        # ----------------------------------------------------
        # PRICE + VOLUME CHART
        # ----------------------------------------------------
        plt.figure(figsize=(14, 6))
        plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

        # Scale volume visually
        vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
        plt.bar(df["Date"], vol_scaled, alpha=0.2, label="Volume")

        plt.title(f"{symbol} Price & Volume")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(price_png)
        plt.close()

        # ----------------------------------------------------
        # MOVING AVERAGE CHART
        # ----------------------------------------------------
        plt.figure(figsize=(14, 6))
        plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
        plt.plot(df["Date"], df["MA20"], label="MA20")
        plt.plot(df["Date"], df["MA50"], label="MA50")

        plt.title(f"{symbol} Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(ma_png)
        plt.close()

        # ----------------------------------------------------
        # TABLE (last 100 rows)
        # ----------------------------------------------------
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

        # ----------------------------------------------------
        # FINAL HTML (FULL DOCUMENT FRAGMENT)
        # ----------------------------------------------------
        html = f"""
<h2>{symbol} – Daily Dashboard</h2>

<h3>Price Table (Last 100 Days)</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr style="background:#eee;font-weight:bold;">
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
<img src="{price_url}" style="width:100%;max-width:1200px;">

<h3>Moving Averages</h3>
<img src="{ma_url}" style="width:100%;max-width:1200px;">
"""

        persist.save(cache_key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
