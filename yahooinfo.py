# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback

# ==============================
# Yahoo Finance info fetch
# ==============================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        if not info or not isinstance(info, dict):
            return {}
        return info
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
    "Company Profile": "🏢"
}

# ==============================
# Column layout wrapper
# ==============================
def column_layout(html, min_width=260):
    return f"""
    <div style="
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax({min_width}px,1fr));
        gap:8px;
        align-items:start;
    ">
        {html}
    </div>
    """

# ==============================
# Card renderer
# ==============================
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
    <div style="
        background:{shades[shade%3]};
        border:1px solid #a3c0e0;
        border-radius:8px;
        padding:{pad};
        font-size:{font};
        box-shadow:0 2px 6px rgba(0,0,0,.08);
    ">
        <div style="
            background:{grads[shade%3]};
            color:white;
            padding:4px 8px;
            border-radius:6px;
            font-weight:600;
            margin-bottom:6px;
        ">
            {title}
        </div>
        {body}
    </div>
    """

# ==============================
# Number formatting
# ==============================
def format_number(x):
    try:
        x = float(x)
        if abs(x) >= 100:
            return f"{x:,.0f}"
        if abs(x) >= 1:
            return f"{x:,.2f}"
        return f"{x:.4f}"
    except:
        return str(x)

# ==============================
# Compact inline table (Field : Value)
# ==============================
def make_table(df):
    rows = ""
    for _, r in df.iterrows():
        val = r[1]
        color = "#0d1f3c"

        # Highlight change values
        if any(x in r[0].lower() for x in ["chg", "%"]):
            try:
                color = "#0a7d32" if float(val) >= 0 else "#b00020"
            except:
                pass

        rows += f"""
        <div style="
            display:flex;
            justify-content:space-between;
            gap:6px;
            padding:2px 0;
            border-bottom:1px dashed #bcd0ea;
        ">
            <span style="color:#1a4f8a;font-weight:500;white-space:nowrap;">
                {r[0]}
            </span>
            <span style="
                color:{color};
                font-weight:600;
                background:#f1f6ff;
                padding:1px 6px;
                border-radius:4px;
                white-space:nowrap;
            ">
                {val}
            </span>
        </div>
        """

    return f"<div>{rows}</div>"

# ==============================
# Noise keys
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

def is_noise(k): 
    return k in NOISE_KEYS

# ==============================
# Duplicate resolution
# ==============================
DUPLICATE_PRIORITY = {
    "price": ["regularMarketPrice","currentPrice"],
    "prev": ["regularMarketPreviousClose","previousClose"],
    "open": ["regularMarketOpen","open"],
    "high": ["regularMarketDayHigh","dayHigh"],
    "low": ["regularMarketDayLow","dayLow"],
    "volume": ["regularMarketVolume","volume"]
}

def resolve_duplicates(data):
    resolved, used = {}, set()
    for keys in DUPLICATE_PRIORITY.values():
        for k in keys:
            if k in data:
                resolved[k] = data[k]
                used.update(keys)
                break
    for k,v in data.items():
        if k not in used:
            resolved[k] = v
    return resolved

# ==============================
# Short names
# ==============================
SHORT_NAMES = {
    "regularMarketPrice":"Price","regularMarketChange":"Chg",
    "regularMarketChangePercent":"Chg%",
    "regularMarketPreviousClose":"Prev",
    "regularMarketOpen":"Open",
    "regularMarketDayHigh":"High","regularMarketDayLow":"Low",
    "regularMarketVolume":"Vol",
    "averageDailyVolume10Day":"AvgV10",
    "averageDailyVolume3Month":"AvgV3M",
    "fiftyDayAverage":"50DMA","twoHundredDayAverage":"200DMA",
    "fiftyTwoWeekLow":"52WL","fiftyTwoWeekHigh":"52WH",
    "beta":"Beta","targetMeanPrice":"Target"
}

def pretty_key(k):
    return SHORT_NAMES.get(k, k[:12])

# ==============================
# Classifiers
# ==============================
def classify_price_volume_subgroup(key):
    k = key.lower()
    if "volume" in k: return "Volume"
    if "average" in k or "dma" in k: return "Moving Avg"
    if "week" in k or "beta" in k: return "Range / Vol"
    if "target" in k or "recommend" in k: return "Bid / Analyst"
    return "Live Price"

def classify_key(key, value):
    k = key.lower()
    if isinstance(value,(int,float)) and any(x in k for x in [
        "price","volume","avg","change","percent","market","week","beta","target"
    ]):
        return "price_volume"
    if any(x in k for x in [
        "revenue","income","profit","margin","pe","pb","roe","roa","debt","equity"
    ]):
        return "fundamental"
    if isinstance(value,str) and len(value)>80:
        return "long_text"
    return "profile"

# ==============================
# Group builder
# ==============================
def build_grouped_info(info):
    groups = {"price_volume":{}, "fundamental":{}, "profile":{}, "long_text":{}}
    for k,v in info.items():
        if v in [None,"",[],{}]: continue
        groups[classify_key(k,v)][k] = v
    return groups

# ==============================
# DataFrame builder
# ==============================
def build_df_from_dict(data):
    rows=[]
    for k,v in data.items():
        if is_noise(k): continue
        if isinstance(v,(int,float)):
            v = format_number(v)
        rows.append([pretty_key(k), v])
    return pd.DataFrame(rows, columns=["Field","Value"])

# ==============================
# MAIN FUNCTION
# ==============================
def fetch_info(symbol):
    try:
        info = yfinfo(symbol)
        if not info:
            return "No data"

        groups = build_grouped_info(info)
        html = ""

        # -------- PRICE / VOLUME --------
        pv = resolve_duplicates(groups["price_volume"])
        sub = {}
        for k,v in pv.items():
            sg = classify_price_volume_subgroup(k)
            sub.setdefault(sg,{})[k] = v

        cards = ""
        for i,(t,d) in enumerate(sub.items()):
            df = build_df_from_dict(d)
            if not df.empty:
                cards += html_card(
                    f"{SUBGROUP_ICONS.get(t,'ℹ️')} {t}",
                    make_table(df),
                    mini=True,
                    shade=i
                )

        if cards:
            html += html_card(
                f"{MAIN_ICONS['Price / Volume']} Price / Volume",
                column_layout(cards),
                shade=0
            )

        # -------- FUNDAMENTALS --------
        if groups["fundamental"]:
            html += html_card(
                f"{MAIN_ICONS['Fundamentals']} Fundamentals",
                make_table(build_df_from_dict(groups["fundamental"])),
                shade=1
            )

        # -------- PROFILE --------
        if groups["profile"]:
            html += html_card(
                f"{MAIN_ICONS['Company Profile']} Company Profile",
                make_table(build_df_from_dict(groups["profile"])),
                shade=2
            )

        # -------- LONG TEXT --------
        for k,v in groups["long_text"].items():
            html += html_card(pretty_key(k), v, shade=2)

        return html

    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>"