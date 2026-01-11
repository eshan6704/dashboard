# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone

from .persist import exists, load, save


# ==============================
# Yahoo Finance fetch
# ==============================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        return {"__error__": str(e)}


# ==============================
# Icons
# ==============================
MAIN_ICONS = {
    "Price / Volume": "📈",
    "Fundamentals": "📊",
    "Trend": "📈",
    "Signals": "🧠",
    "Company Profile": "🏢",
    "Management": "👔"
}


# ==============================
# Layout helpers
# ==============================
def column_layout(html):
    return f"""
    <style>
        .grid {{
            display:grid;
            gap:10px;
            grid-template-columns:repeat(3,1fr);
        }}
        @media(max-width:1024px) {{
            .grid {{ grid-template-columns:repeat(2,1fr); }}
        }}
        @media(max-width:640px) {{
            .grid {{ grid-template-columns:1fr; }}
        }}
        .pos {{ color:#0a7d32;font-weight:600; }}
        .neg {{ color:#b00020;font-weight:600; }}
    </style>
    <div class="grid">{html}</div>
    """


def collapsible(title, body):
    return f"""
    <details open>
        <summary style="cursor:pointer;font-weight:600;font-size:15px;padding:6px 0;">
            {title}
        </summary>
        {body}
    </details>
    """


def html_card(title, body, mini=False, shade=0):
    font = "12px" if mini else "14px"
    pad  = "6px" if mini else "10px"
    shades = ["#e6f0fa","#d7e3f5","#c8d6f0"]

    return f"""
    <div style="background:{shades[shade%3]};
                border:1px solid #a3c0e0;
                border-radius:8px;
                padding:{pad};
                font-size:{font};">
        <div style="font-weight:600;margin-bottom:6px;">
            {title}
        </div>
        {body}
    </div>
    """


# ==============================
# Formatting helpers
# ==============================
def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e7: return f"{n/1e7:.2f}Cr"
        if abs(n) >= 1e5: return f"{n/1e5:.2f}L"
        if abs(n) >= 1e3: return f"{n/1e3:.2f}K"
        return f"{n:,.2f}"
    except:
        return str(n)


# ---------- DATE FIX (ROBUST) ----------
DATE_KEYWORDS = (
    "date", "time", "timestamp",
    "fiscal", "quarter",
    "earnings", "dividend"
)

def looks_like_unix_ts(v):
    try:
        v = int(v)
        return (
            946684800 <= v <= 4102444800 or       # seconds
            946684800000 <= v <= 4102444800000   # milliseconds
        )
    except:
        return False


def unix_to_date(v):
    try:
        v = int(v)
        if v > 10**12:
            v //= 1000
        return datetime.fromtimestamp(v, tz=timezone.utc).strftime("%d %b %Y")
    except:
        return v


def format_value(k, v):
    lk = k.lower()

    # --- DATE HANDLING ---
    if isinstance(v, (int, float)) and looks_like_unix_ts(v):
        if any(x in lk for x in DATE_KEYWORDS):
            return unix_to_date(v)

    # --- NUMBERS ---
    if isinstance(v, (int, float)):
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        if "percent" in lk:
            return f'<span class="{cls}">{v:.2f}%</span>'
        if any(x in lk for x in [
            "marketcap","revenue","income",
            "value","cap","enterprise"
        ]):
            return f'<span class="{cls}">₹{human_number(v)}</span>'
        return f'<span class="{cls}">{human_number(v)}</span>'

    return v


def make_table(df):
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;
                    border-bottom:1px dashed #bcd0ea;padding:2px 0;">
            <span>{r.Field}</span>
            <span>{r.Value}</span>
        </div>
        """
        for r in df.itertuples()
    )


# ==============================
# Keys
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

SHORT_NAMES = {
    "regularMarketPrice":"Price",
    "regularMarketChange":"Chg",
    "regularMarketChangePercent":"Chg%",
    "regularMarketOpen":"Open",
    "regularMarketDayHigh":"High",
    "regularMarketDayLow":"Low",
    "regularMarketVolume":"Vol",
    "marketCap":"MCap",
    "trailingPE":"PE",
    "forwardPE":"FwdPE",
    "priceToBook":"PB",
    "epsTrailingTwelveMonths":"EPS",
    "returnOnEquity":"ROE",
    "returnOnAssets":"ROA",
    "profitMargins":"Margin",
    "debtToEquity":"D/E",
    "mostRecentQuarter":"Recent Q",
    "lastFiscalYearEnd":"FY End",
    "nextFiscalYearEnd":"Next FY"
}

PIN_PRICE = ["Price","Chg","Chg%","Open","High","Low","Vol"]
PIN_FUND  = ["MCap","PE","PB","EPS","ROE","ROA","Margin","D/E"]

def pretty_key(k):
    return SHORT_NAMES.get(k, k[:16])


# ==============================
# Classification
# ==============================
def classify(k, v):
    lk = k.lower()
    if k == "companyOfficers":
        return "management"
    if any(x in lk for x in [
        "pe","pb","roe","roa","margin",
        "debt","revenue","profit","eps","cap"
    ]):
        return "fundamental"
    if isinstance(v, (int, float)):
        return "price_volume"
    if isinstance(v, str) and len(v) > 80:
        return "long_text"
    return "profile"


def group_info(info):
    g = {
        "price_volume": {},
        "fundamental": {},
        "profile": {},
        "management": {},
        "long_text": {}
    }
    for k,v in info.items():
        if k in NOISE_KEYS or v in [None,"",[],{}]:
            continue
        g[classify(k,v)][k] = v
    return g


# ==============================
# Builders
# ==============================
def build_df(data, pinned=None):
    rows = [(pretty_key(k), format_value(k,v)) for k,v in data.items()]
    pinned = pinned or []
    rows.sort(key=lambda x: (
        0 if x[0] in pinned else 1,
        pinned.index(x[0]) if x[0] in pinned else x[0]
    ))
    return pd.DataFrame(rows, columns=["Field","Value"])


def split_df(df):
    n = len(df)
    cols = 1 if n <= 6 else 2 if n <= 14 else 3
    size = (n + cols - 1) // cols
    return [df.iloc[i:i+size] for i in range(0, n, size)]


# ==============================
# Trend & Signals
# ==============================
def build_trend(info):
    rows = []
    p = info.get("regularMarketPrice")
    l = info.get("fiftyTwoWeekLow")
    h = info.get("fiftyTwoWeekHigh")
    d50 = info.get("fiftyDayAverage")
    beta = info.get("beta")

    if p and l and h:
        rows.append(("52W Position", f"{(p-l)/(h-l)*100:.1f}%"))
    if p and d50:
        rows.append(("vs 50DMA", "Above ↑" if p>d50 else "Below ↓"))
    if beta:
        rows.append(("Risk", "High" if beta>1.3 else "Low" if beta<0.8 else "Moderate"))

    return pd.DataFrame(rows, columns=["Field","Value"])


def build_signals(info):
    rows = []
    pe = info.get("trailingPE")
    roe = info.get("returnOnEquity")
    p = info.get("regularMarketPrice")
    d50 = info.get("fiftyDayAverage")

    if pe:
        rows.append(("Valuation","Expensive" if pe>35 else "Cheap" if pe<15 else "Fair"))
    if p and d50:
        rows.append(("Momentum","Strong" if p>d50 else "Weak"))
    if roe:
        rows.append(("Quality","High" if roe>0.18 else "Average"))

    return pd.DataFrame(rows, columns=["Field","Value"])


# ==============================
# MAIN
# ==============================
def fetch_info(symbol):
    key = f"info_{symbol}"

    if exists(key,"html"):
        cached = load(key,"html")
        if cached:
            return cached

    try:
        info = yfinfo(symbol)
        if "__error__" in info:
            return "No data"

        g = group_info(info)
        html = ""

        if g["price_volume"]:
            df = build_df(g["price_volume"], PIN_PRICE)
            html += collapsible(
                f"{MAIN_ICONS['Price / Volume']} Price / Volume",
                column_layout("".join(
                    html_card("Price", make_table(c), mini=True)
                    for c in split_df(df)
                ))
            )

        if g["fundamental"]:
            df = build_df(g["fundamental"], PIN_FUND)
            html += collapsible(
                f"{MAIN_ICONS['Fundamentals']} Fundamentals",
                column_layout("".join(
                    html_card("Fundamentals", make_table(c), mini=True)
                    for c in split_df(df)
                ))
            )

        trend = build_trend(info)
        if not trend.empty:
            html += collapsible(
                f"{MAIN_ICONS['Trend']} Trend Summary",
                html_card("Trend", make_table(trend), mini=True)
            )

        sig = build_signals(info)
        if not sig.empty:
            html += collapsible(
                f"{MAIN_ICONS['Signals']} Smart Signals",
                html_card("Signals", make_table(sig), mini=True)
            )

        if g["profile"]:
            df = build_df(g["profile"])
            html += collapsible(
                f"{MAIN_ICONS['Company Profile']} Company Profile",
                column_layout("".join(
                    html_card("Profile", make_table(c), mini=True)
                    for c in split_df(df)
                ))
            )

        if g["management"].get("companyOfficers"):
            cards = ""
            for o in g["management"]["companyOfficers"]:
                cards += html_card(
                    o.get("name",""),
                    o.get("title",""),
                    mini=True
                )
            html += collapsible(
                f"{MAIN_ICONS['Management']} Management",
                column_layout(cards)
            )

        for k,v in g["long_text"].items():
            html += collapsible(pretty_key(k), v)

        save(key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
