# daily.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import traceback
import io

from . import persist
from . import backblaze as b2


# ============================================================
# CONFIG
# ============================================================
IMAGE_FORMAT = "png"
IMAGE_EXT = "png"
DPI = 150


# ============================================================
# MAIN
# ============================================================
def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        # ----------------------------------------------------
        # Date conversion
        # ----------------------------------------------------
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        # ----------------------------------------------------
        # Fetch daily data
        # ----------------------------------------------------
        df = yf.download(symbol + ".NS", start=start, end=end)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return "<h3>No daily data found</h3>"

        # ----------------------------------------------------
        # Clean data
        # ----------------------------------------------------
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna()
        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # ----------------------------------------------------
        # Indicators
        # ----------------------------------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        # ====================================================
        # PRICE + VOLUME CHART
        # ====================================================
        buf = io.BytesIO()

        plt.figure(figsize=(14, 6))
        plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

        vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
        plt.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")

        plt.title(f"{symbol} Price & Volume")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(
            buf,
            format=IMAGE_FORMAT,
            dpi=DPI,
            bbox_inches="tight"
        )
        plt.close()

        buf.seek(0)
        price_key = f"daily/{symbol}_price_volume.{IMAGE_EXT}"
        b2.upload_file("eshanhf", price_key, buf.getvalue())
        price_url = f"{b2.S3_ENDPOINT}/eshanhf/{price_key}"

        # ====================================================
        # MOVING AVERAGE CHART
        # ====================================================
        buf = io.BytesIO()

        plt.figure(figsize=(14, 6))
        plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
        plt.plot(df["Date"], df["MA20"], label="MA20")
        plt.plot(df["Date"], df["MA50"], label="MA50")

        plt.title(f"{symbol} Moving Averages")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(
            buf,
            format=IMAGE_FORMAT,
            dpi=DPI,
            bbox_inches="tight"
        )
        plt.close()

        buf.seek(0)
        ma_key = f"daily/{symbol}_ma.{IMAGE_EXT}"
        b2.upload_file("eshanhf", ma_key, buf.getvalue())
        ma_url = f"{b2.S3_ENDPOINT}/eshanhf/{ma_key}"

        # ====================================================
        # TABLE (Last 100 days)
        # ====================================================
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

        # ====================================================
        # FINAL HTML
        # ====================================================
        html = f"""
<div id="daily_dashboard">

<h2>{symbol} – Daily Analysis</h2>

<h3>Price Table (Last 100 Days)</h3>
<table style="border-collapse:collapse;width:100%;" border="1" cellpadding="6">
<tr style="background:#f0f0f0;font-weight:bold;">
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

</div>
"""

        persist.save(key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"