# daily.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import traceback
import io
import time

from . import persist
from . import backblaze as b2


# ============================================================
# CONFIG
# ============================================================
IMAGE_FORMAT = "png"
IMAGE_EXT = "png"
DPI = 150
IMAGE_QUALITY = 85   # compression quality (PNG is lossless)

# Public download base (DISPLAY ONLY, no change to backblaze.py)
B2_PUBLIC_BASE = "https://f005.backblazeb2.com/file/eshanhf"
# ⚠️ replace f005 if your Backblaze console shows different


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
        # Fetch data
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

        plt.savefig(buf, format=IMAGE_FORMAT, dpi=DPI, bbox_inches="tight")
        plt.close()

        buf.seek(0)
        price_key = f"daily/{symbol}_price_volume.{IMAGE_EXT}"

        b2.upload_image_compressed(
            "eshanhf",
            price_key,
            buf.getvalue(),
            quality=IMAGE_QUALITY
        )

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

        plt.savefig(buf, format=IMAGE_FORMAT, dpi=DPI, bbox_inches="tight")
        plt.close()

        buf.seek(0)
        ma_key = f"daily/{symbol}_ma.{IMAGE_EXT}"

        b2.upload_image_compressed(
            "eshanhf",
            ma_key,
            buf.getvalue(),
            quality=IMAGE_QUALITY
        )

        # ----------------------------------------------------
        # Cache-busting timestamp
        # ----------------------------------------------------
        ts = int(time.time())
        price_url = f"{B2_PUBLIC_BASE}/{price_key}?v={ts}"
        ma_url    = f"{B2_PUBLIC_BASE}/{ma_key}?v={ts}"

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
        # FINAL HTML (IMAGE WAIT + RETRY)
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
<img data-src="{price_url}" style="width:100%;max-width:1200px;">

<h3>Moving Averages</h3>
<img data-src="{ma_url}" style="width:100%;max-width:1200px;">

<script>
function loadWithRetry(img, retries = 6, delay = 800) {{
    let attempt = 0;

    function tryLoad() {{
        attempt++;
        img.src = img.dataset.src + "&retry=" + attempt;
    }}

    img.onerror = function() {{
        if (attempt < retries) {{
            setTimeout(tryLoad, delay);
        }} else {{
            img.alt = "Image failed to load";
        }}
    }};

    tryLoad();
}}

document.querySelectorAll("img[data-src]").forEach(img => {{
    loadWithRetry(img);
}});
</script>

</div>
"""

        persist.save(key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"