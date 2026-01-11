# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone

# persist helpers
from .persist import exists, load, save


# ==============================
# Yahoo Finance info fetch (RAW)
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
SUBGROUP_ICONS = {
    "Live Price": "💹",
    "Volume": "📊",
    "Moving Avg": "📈",
    "Range / Vol": "📉",
    "Bid / Analyst": "📝",
    "Other": "ℹ️"
}

MAIN_ICONS = {
    "Price / Volume": "📈",
    "Fundamentals": "📊",
    "Company Profile": "🏢",
    "Management": "👔"
}


# ==============================
# Layout helpers
# ==============================
def column_layout(html, min_width=320):
    return f"""
    <div style="display:grid;
                grid-template-columns:repeat(auto-fit,minmax({min_width}px,1fr));
                gap:10px;">
        {html}
    </div>
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
        abs_n = abs(n)
        if abs_n >= 1e7:
            return f"{n/1e7:.2f}Cr"
        if abs_n >= 1e5:
            return f"{n/1e5:.2f}L"
        if abs_n >= 1e3:
            return f"{n/1e3:.2f}K"
        return f"{n:,.2f}"
    except:
        return str(n)


def format_date(v):
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc).strftime("%d %b %Y")
        if isinstance(v, str) and v.isdigit():
            return datetime.fromtimestamp(int(v), tz=timezone.utc).strftime("%d %b %Y")
        return v
    except:
        return v


def format_value(k, v):
    lk = k.lower()

    if isinstance(v, (int, float)):
        if "percent" in lk or "yield" in lk:
            return f"{v:.2f}%"
        if "marketcap" in lk or "revenue" in lk or "income" in lk:
            return "₹" + human_number(v)
        return human_number(v)

    if "date" in lk or "time" in lk:
        return format_date(v)

    return v


# ==============================
# Compact table
# ==============================
def make_table(df):
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;
                    border-bottom:1px dashed #bcd0ea;padding:2px 0;">
            <span style="color:#1a4f8a;">{r.Field}</span>
            <span style="font-weight:600;">{r.Value}</span>
        </div>
        """
        for r in df.itertuples()
    )


# ==============================
# Noise
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

def is_noise(k): return k in NOISE_KEYS


# ==============================
# Short display names
# ==============================
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

def pretty_key(k): return SHORT_NAMES.get(k, k[:14])


# ==============================
# Classifiers
# ==============================
def classify_key(k, v):
    lk = k.lower()
    if k == "companyOfficers":
        return "management"
    if isinstance(v,(int,float)):
        return "price_volume"
    if isinstance(v,str) and len(v) > 80:
        return "long_text"
    return "profile"


# ==============================
# Group builder
# ==============================
def build_grouped_info(info):
    g = {"price_volume":{}, "profile":{}, "long_text":{}, "management":{}}
    for k,v in info.items():
        if v in [None,"",[],{}]: continue
        g[classify_key(k,v)][k] = v
    return g


# ==============================
# DF builder (sorted by display name)
# ==============================
def build_df_from_dict(data):
    rows = []
    for k,v in data.items():
        if is_noise(k): continue
        rows.append((pretty_key(k), format_value(k,v)))
    rows.sort(key=lambda x: x[0].lower())
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

        groups = build_grouped_info(info)
        html = ""

        # Price / Volume
        if groups["price_volume"]:
            html += html_card(
                f"{MAIN_ICONS['Price / Volume']} Price / Volume",
                make_table(build_df_from_dict(groups["price_volume"]))
            )

        # Profile
        if groups["profile"]:
            html += html_card(
                f"{MAIN_ICONS['Company Profile']} Company Profile",
                make_table(build_df_from_dict(groups["profile"]))
            )

        # Management (companyOfficers)
        if groups["management"].get("companyOfficers"):
            officers = ""
            for o in groups["management"]["companyOfficers"]:
                officers += html_card(
                    o.get("name",""),
                    f"{o.get('title','')}<br/>Pay: ₹{human_number(o.get('totalPay',0))}",
                    mini=True
                )

            html += html_card(
                f"{MAIN_ICONS['Management']} Management",
                column_layout(officers)
            )

        # Long text
        for k,v in groups["long_text"].items():
            html += html_card(pretty_key(k), v)

        if html.strip():
            save(key, html, "html")

        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
