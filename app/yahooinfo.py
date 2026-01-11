# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone

from .persist import exists, load, save


# ==============================
# Yahoo Finance info fetch
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
    "Company Profile": "🏢",
    "Management": "👔"
}


# ==============================
# Responsive layout
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
        .pos {{ color:#0a7d32; font-weight:600; }}
        .neg {{ color:#b00020; font-weight:600; }}
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

    shades = ["#e6f0fa", "#d7e3f5", "#c8d6f0"]
    grads = [
        "linear-gradient(to right,#1a4f8a,#4a7ac7)",
        "linear-gradient(to right,#1f5595,#5584d6)",
        "linear-gradient(to right,#205ca0,#6192e0)"
    ]

    return f"""
    <div style="background:{shades[shade%3]};
                border:1px solid #a3c0e0;
                border-radius:8px;
                padding:{pad};
                font-size:{font};">
        <div style="background:{grads[shade%3]};
                    color:white;
                    padding:4px 8px;
                    border-radius:6px;
                    font-weight:600;
                    margin-bottom:6px;">
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


def format_date(v):
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc).strftime("%d %b %Y")
        return v
    except:
        return v


def format_value(k, v):
    lk = k.lower()
    arrow = ""
    cls = ""

    if isinstance(v, (int, float)):
        if v > 0: cls, arrow = "pos", "↑"
        elif v < 0: cls, arrow = "neg", "↓"

        if "percent" in lk:
            return f'<span class="{cls}">{arrow}{v:.2f}%</span>'
        if "marketcap" in lk:
            return f'<span class="{cls}">₹{human_number(v)}</span>'
        return f'<span class="{cls}">{human_number(v)}</span>'

    if "date" in lk or "time" in lk:
        return format_date(v)

    return v


# ==============================
# Table renderer
# ==============================
def make_table(df):
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;
                    border-bottom:1px dashed #bcd0ea;padding:2px 0;">
            <span style="color:#1a4f8a;">{r.Field}</span>
            <span>{r.Value}</span>
        </div>
        """
        for r in df.itertuples()
    )


# ==============================
# Utils
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

def is_noise(k): return k in NOISE_KEYS


SHORT_NAMES = {
    "regularMarketPrice":"Price",
    "regularMarketChange":"Chg",
    "regularMarketChangePercent":"Chg%",
    "regularMarketPreviousClose":"Prev",
    "regularMarketOpen":"Open",
    "regularMarketDayHigh":"High",
    "regularMarketDayLow":"Low",
    "regularMarketVolume":"Vol",
    "marketCap":"MCap",
    "beta":"Beta",
    "targetMeanPrice":"Target"
}

# 🔑 USER CONFIGURABLE
PINNED_FIELDS = [
    "Price","Chg","Chg%","Open","High","Low","Vol","MCap","Beta"
]

def pretty_key(k): return SHORT_NAMES.get(k, k[:14])


# ==============================
# Grouping
# ==============================
def classify_key(k, v):
    if k == "companyOfficers":
        return "management"
    if isinstance(v, (int, float)):
        return "price_volume"
    if isinstance(v, str) and len(v) > 80:
        return "long_text"
    return "profile"


def build_grouped_info(info):
    g = {
        "price_volume": {},
        "profile": {},
        "management": {},
        "long_text": {}
    }
    for k, v in info.items():
        if v in [None, "", [], {}]:
            continue
        g[classify_key(k, v)][k] = v
    return g


# ==============================
# Column splitter
# ==============================
def split_df_evenly(df):
    if df.empty: return []
    n = len(df)
    cols = 1 if n <= 6 else 2 if n <= 14 else 3
    chunk = (n + cols - 1) // cols
    return [df.iloc[i:i+chunk] for i in range(0, n, chunk)]


# ==============================
# DF builder (PIN + SORT)
# ==============================
def build_df_from_dict(data):
    rows = []
    for k, v in data.items():
        if is_noise(k): continue
        label = pretty_key(k)
        rows.append((label, format_value(k, v)))

    rows.sort(
        key=lambda x: (
            0 if x[0] in PINNED_FIELDS else 1,
            PINNED_FIELDS.index(x[0]) if x[0] in PINNED_FIELDS else x[0].lower()
        )
    )

    return pd.DataFrame(rows, columns=["Field","Value"])


# ==============================
# MAIN
# ==============================
def fetch_info(symbol):
    key = f"info_{symbol}"

    if exists(key, "html"):
        cached = load(key, "html")
        if cached:
            return cached

    try:
        info = yfinfo(symbol)
        if "__error__" in info:
            return "No data"

        g = build_grouped_info(info)
        html = ""

        # PRICE / VOLUME
        if g["price_volume"]:
            df = build_df_from_dict(g["price_volume"])
            cols = "".join(
                html_card("📈 Price & Volume", make_table(c), mini=True, shade=i)
                for i,c in enumerate(split_df_evenly(df))
            )
            html += collapsible(
                f"{MAIN_ICONS['Price / Volume']} Price / Volume",
                column_layout(cols)
            )

        # COMPANY PROFILE
        if g["profile"]:
            df = build_df_from_dict(g["profile"])
            cols = "".join(
                html_card("🏢 Profile", make_table(c), mini=True, shade=i)
                for i,c in enumerate(split_df_evenly(df))
            )
            html += collapsible(
                f"{MAIN_ICONS['Company Profile']} Company Profile",
                column_layout(cols)
            )

        # MANAGEMENT
        if g["management"].get("companyOfficers"):
            officers = ""
            for o in g["management"]["companyOfficers"]:
                officers += html_card(
                    o.get("name",""),
                    f"{o.get('title','')}<br/>Pay: ₹{human_number(o.get('totalPay',0))}",
                    mini=True
                )
            html += collapsible(
                f"{MAIN_ICONS['Management']} Management",
                column_layout(officers)
            )

        # LONG TEXT
        for k,v in g["long_text"].items():
            html += collapsible(pretty_key(k), v)

        if html.strip():
            save(key, html, "html")

        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
