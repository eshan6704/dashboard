'''
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
        '''
# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback


# ======================================================
# INLINE SVG BUILDER (TEMP – MOVE LATER IF YOU WANT)
# ======================================================

class SVG:
    def __init__(self, width, height, bg="#0e1117"):
        self.width = width
        self.height = height
        self.bg = bg
        self.e = []

    def line(self, x1, y1, x2, y2, stroke="#888", w=1):
        self.e.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{w}"/>'
        )

    def rect(self, x, y, w, h, fill):
        self.e.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
        )

    def text(self, x, y, t, size=11, color="#888", anchor="start"):
        self.e.append(
            f'<text x="{x}" y="{y}" fill="{color}" '
            f'font-size="{size}" text-anchor="{anchor}">{t}</text>'
        )

    def raw(self, s):
        self.e.append(s)

    def render(self):
        return (
            f'<svg width="{self.width}" height="{self.height}" '
            f'style="background:{self.bg}">\n' +
            "\n".join(self.e) +
            "\n</svg>"
        )


# ======================================================
# SVG PRICE + VOLUME CANDLESTICK
# ======================================================

def build_price_volume_svg(df, symbol):
    W, H = 1200, 520

    PAD_L = 80
    PAD_R = 40
    PAD_T = 40
    PAD_B = 120

    PRICE_H = H - PAD_T - PAD_B
    VOL_H = 80
    VOL_Y = PAD_T + PRICE_H + 20

    svg = SVG(W, H)

    prices = df["High"].tolist() + df["Low"].tolist()
    pmin, pmax = min(prices), max(prices)
    vmax = df["Volume"].max()

    def y_price(p):
        return PAD_T + (pmax - p) / (pmax - pmin) * PRICE_H

    def y_vol(v):
        return VOL_Y + VOL_H - (v / vmax) * VOL_H

    # -------- AXIS --------
    svg.line(PAD_L, PAD_T, PAD_L, PAD_T + PRICE_H, "#555")
    svg.line(PAD_L, PAD_T + PRICE_H, W - PAD_R, PAD_T + PRICE_H, "#555")

    # -------- GRID + PRICE LABELS --------
    for i in range(5):
        y = PAD_T + i * PRICE_H / 4
        price = pmax - i * (pmax - pmin) / 4
        svg.line(PAD_L, y, W - PAD_R, y, "#222")
        svg.text(10, y + 4, f"{price:.0f}")

    svg.text(10, VOL_Y + VOL_H / 2, "Volume")

    step = (W - PAD_L - PAD_R) / len(df)
    cw = step * 0.6

    for i, r in enumerate(df.itertuples()):
        x = PAD_L + i * step + step / 2

        o, h, l, c = r.Open, r.High, r.Low, r.Close
        color = "#2ecc71" if c >= o else "#e74c3c"

        # Wick
        svg.line(x, y_price(h), x, y_price(l), color)

        # Body
        top = y_price(max(o, c))
        bh = abs(y_price(o) - y_price(c))
        bh = max(bh, 1)
        svg.rect(x - cw / 2, top, cw, bh, color)

        # Volume
        vh = VOL_Y + VOL_H - y_vol(r.Volume)
        svg.rect(x - cw / 2, y_vol(r.Volume), cw, vh, color)

        # Tooltip
        svg.raw(
            f'<title>{r.DateStr} | '
            f'O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} '
            f'V:{int(r.Volume)}</title>'
        )

    # -------- X AXIS LABELS --------
    skip = max(1, len(df) // 6)
    for i in range(0, len(df), skip):
        x = PAD_L + i * step + step / 2
        svg.text(x, H - 10, df.iloc[i]["DateStr"], anchor="middle")

    return svg.render()


# ======================================================
# MAIN DAILY FETCH FUNCTION
# ======================================================

def fetch_daily(symbol, date_end, date_start):
    try:
        start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")

        df = yf.download(symbol + ".NS", start=start, end=end)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return "<h3>No daily data found</h3>"

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

        # Limit rows for rendering
        view = df.tail(100)

        # SVG
        price_svg = build_price_volume_svg(view, symbol)

        # Table
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

        html = f"""
<div style="background:#0e1117;color:#e6e6e6;font-family:Arial;padding:10px">

<h2>{symbol} – Daily Dashboard</h2>

<h3>Price & Volume</h3>
{price_svg}

<h3>Historical Data (Last 100 Days)</h3>
<table border="1" cellpadding="6" width="100%" style="border-collapse:collapse">
<tr style="background:#161b22">
<th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>
</tr>
{rows}
</table>

</div>
"""

        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
