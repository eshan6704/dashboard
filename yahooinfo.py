
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
        t = yf.Ticker(symbol)
        info = t.info
        if not info or not isinstance(info, dict):
            return {}
        return info
    except Exception as e:
        return {"__error__": str(e)}


# ==============================
# HTML card renderer
# ==============================
def html_card(title, body, mini=False):
    font = "12px" if mini else "14px"
    pad  = "6px" if mini else "10px"

    return f"""
    <div style="
        background:#111;
        border:1px solid #333;
        border-radius:6px;
        padding:{pad};
        margin:6px 0;
        color:#eee;
        font-size:{font};
    ">
        <div style="
            font-weight:600;
            color:#6cf;
            margin-bottom:4px;
        ">
            {title}
        </div>
        <div>{body}</div>
    </div>
    """


# ==============================
# DataFrame → HTML table
# ==============================
def make_table(df, compact=False):
    if df is None or df.empty:
        return "<i>No data</i>"

    font = "11px" if compact else "13px"
    pad  = "2px 6px" if compact else "4px 8px"

    th = "".join(
        f"<th style='padding:{pad};border-bottom:1px solid #444'>{c}</th>"
        for c in df.columns
    )

    rows = ""
    for _, r in df.iterrows():
        tds = "".join(
            f"<td style='padding:{pad};border-bottom:1px solid #222'>{v}</td>"
            for v in r
        )
        rows += f"<tr>{tds}</tr>"

    return f"""
    <table style="
        width:100%;
        border-collapse:collapse;
        font-size:{font};
        color:#eee;
    ">
        <thead><tr>{th}</tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """


# ==============================
# Number formatting
# ==============================
def format_number(x):
    try:
        if x is None:
            return "-"
        x = float(x)
        if abs(x) >= 100:
            return f"{x:,.0f}"
        if abs(x) >= 1:
            return f"{x:,.2f}"
        return f"{x:.4f}"
    except Exception:
        return str(x)


def format_large_number(x):
    try:
        x = float(x)
        for u in ["", "K", "M", "B", "T"]:
            if abs(x) < 1000:
                return f"{x:.2f}{u}"
            x /= 1000
        return f"{x:.2f}P"
    except Exception:
        return str(x)


# ==============================
# HTML error block
# ==============================
def html_error(msg):
    return f"""
    <div style="
        background:#300;
        color:#f88;
        border:1px solid #800;
        border-radius:6px;
        padding:10px;
        font-weight:600;
    ">
        ❌ {msg}
    </div>
    """
# ------------------------------------------------------------
# 1. Noise keys (internal Yahoo junk)
# ------------------------------------------------------------
NOISE_KEYS = {
    "maxAge", "priceHint", "triggerable",
    "customPriceAlertConfidence",
    "sourceInterval", "exchangeDataDelayedBy",
    "esgPopulated"
}

def is_noise(k):
    return k in NOISE_KEYS


# ------------------------------------------------------------
# 2. Duplicate resolution priority
# ------------------------------------------------------------
DUPLICATE_PRIORITY = {
    "price": ["regularMarketPrice", "currentPrice"],
    "prev": ["regularMarketPreviousClose", "previousClose"],
    "open": ["regularMarketOpen", "open"],
    "high": ["regularMarketDayHigh", "dayHigh"],
    "low": ["regularMarketDayLow", "dayLow"],
    "volume": ["regularMarketVolume", "volume"],
}

def resolve_duplicates(data):
    resolved = {}
    used = set()

    for _, keys in DUPLICATE_PRIORITY.items():
        for k in keys:
            if k in data:
                resolved[k] = data[k]
                used.update(keys)
                break

    for k, v in data.items():
        if k not in used:
            resolved[k] = v

    return resolved


# ------------------------------------------------------------
# 3. Short display names (<=12 chars)
# ------------------------------------------------------------
SHORT_NAMES = {
    "regularMarketPrice": "Price",
    "regularMarketChange": "Chg",
    "regularMarketChangePercent": "Chg%",
    "regularMarketPreviousClose": "Prev",
    "regularMarketOpen": "Open",
    "regularMarketDayHigh": "High",
    "regularMarketDayLow": "Low",

    "regularMarketVolume": "Vol",
    "averageDailyVolume10Day": "AvgV10",
    "averageDailyVolume3Month": "AvgV3M",

    "fiftyDayAverage": "50DMA",
    "fiftyDayAverageChangePercent": "50DMA%",
    "twoHundredDayAverage": "200DMA",
    "twoHundredDayAverageChangePercent": "200DMA%",

    "fiftyTwoWeekLow": "52WL",
    "fiftyTwoWeekHigh": "52WH",
    "fiftyTwoWeekRange": "52WR",

    "beta": "Beta",

    "targetHighPrice": "TgtH",
    "targetLowPrice": "TgtL",
    "targetMeanPrice": "Tgt",
    "recommendationMean": "Reco",
}

def pretty_key(k):
    return SHORT_NAMES.get(k, k[:12])


# ------------------------------------------------------------
# 4. Price / Volume sub-group classifier
# ------------------------------------------------------------
def classify_price_volume_subgroup(key):
    k = key.lower()

    if any(x in k for x in [
        "price", "open", "close", "change", "day"
    ]):
        return "Live Price"

    if "volume" in k:
        return "Volume"

    if "average" in k or "fiftyday" in k or "twohundredday" in k:
        return "Moving Avg"

    if any(x in k for x in ["week", "range", "high", "low", "alltime", "beta"]):
        return "Range / Vol"

    if any(x in k for x in ["bid", "ask", "target", "recommendation", "analyst"]):
        return "Bid / Analyst"

    return "Other"


def build_price_volume_subgroups(data):
    sub = {}
    for k, v in data.items():
        sg = classify_price_volume_subgroup(k)
        sub.setdefault(sg, {})[k] = v
    return sub


# ------------------------------------------------------------
# 5. Main key classifier
# ------------------------------------------------------------
def classify_key(key, value):
    k = key.lower()

    if isinstance(value, str) and len(value) > 80:
        return "long_text"

    if isinstance(value, (int, float)) and any(x in k for x in [
        "price", "volume", "avg", "average", "change",
        "percent", "market", "day", "week", "bid",
        "ask", "beta", "target", "recommendation"
    ]):
        return "price_volume"

    if any(x in k for x in [
        "revenue", "income", "earnings", "profit",
        "margin", "pe", "pb", "roe", "roa",
        "cash", "debt", "equity", "dividend",
        "ebitda", "growth", "ratio", "shares"
    ]):
        return "fundamental"

    return "profile"


# ------------------------------------------------------------
# 6. Group builder
# ------------------------------------------------------------
def build_grouped_info(info):
    groups = {
        "price_volume": {},
        "fundamental": {},
        "profile": {},
        "long_text": {}
    }

    for k, v in info.items():
        if v in [None, "", [], {}]:
            continue

        grp = classify_key(k, v)
        groups[grp][k] = v

    return groups


# ------------------------------------------------------------
# 7. Final DataFrame builder
# ------------------------------------------------------------
def build_df_from_dict(data):
    rows = []

    for k, v in data.items():
        if is_noise(k):
            continue

        if isinstance(v, (int, float)):
            v = format_number(v)
        elif isinstance(v, list):
            v = ", ".join(map(str, v[:5]))

        rows.append([pretty_key(k), v])

    return pd.DataFrame(rows, columns=["Field", "Value"])


# ------------------------------------------------------------
# 8. MAIN FUNCTION (NAME UNCHANGED)
# ------------------------------------------------------------
def fetch_info(symbol):
    try:
        info = yfinfo(symbol)
        if not info:
            return html_error(f"No information found for {symbol}")

        groups = build_grouped_info(info)

        final_html = ""

        # ---------------- PRICE / VOLUME ----------------
        price_data = groups["price_volume"]
        price_data = resolve_duplicates(price_data)

        price_subgroups = build_price_volume_subgroups(price_data)

        price_html = ""
        for title, data in price_subgroups.items():
            df = build_df_from_dict(data)
            if not df.empty:
                price_html += html_card(
                    title,
                    make_table(df, compact=True),
                    mini=True
                )

        if price_html:
            final_html += html_card("📈 Price / Volume", price_html)

        # ---------------- FUNDAMENTALS ----------------
        if groups["fundamental"]:
            df = build_df_from_dict(groups["fundamental"])
            final_html += html_card(
                "📊 Fundamentals",
                make_table(df, compact=True)
            )

        # ---------------- PROFILE ----------------
        if groups["profile"]:
            df = build_df_from_dict(groups["profile"])
            final_html += html_card(
                "🏢 Company Profile",
                make_table(df, compact=True)
            )

        # ---------------- LONG TEXT ----------------
        for k, v in groups["long_text"].items():
            final_html += html_card(
                pretty_key(k),
                f"<div class='long-text'>{v}</div>"
            )

        return final_html

    except Exception as e:
        return html_error(
            f"INFO ERROR: {e}<br><pre>{traceback.format_exc()}</pre>"
        )