# ======================================================
# FINAL YAHOO FINANCE INFO PROCESSOR + RENDERER
# ======================================================

import yfinance as yf
import pandas as pd
import traceback
import re
from datetime import datetime, UTC
from math import floor

from .persist import exists, load, save


# ======================================================
# CONSTANTS
# ======================================================
CR  = 10_000_000
KCR = 10_000_000_000
LCR = 10_000_000_000_000

DATE_KEYS = ("date", "timestamp", "time", "yearend")


# ======================================================
# RAW YAHOO FETCH
# ======================================================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        return {"__error__": str(e)}


# ======================================================
# HELPERS
# ======================================================
def truncate(num, decimals=4):
    f = 10 ** decimals
    return floor(num * f) / f


def compress_key(key, used):
    if len(key) <= 10:
        used.add(key)
        return key

    parts = re.findall(r"[A-Z][a-z]*|[a-z]+", key)
    base = "".join(p[:3] for p in parts)

    if base not in used:
        used.add(base)
        return base

    i = 1
    while f"{base}_{i}" in used:
        i += 1

    final = f"{base}_{i}"
    used.add(final)
    return final


# ======================================================
# CORE PROCESSOR
# ======================================================
def process_info(info):
    main = {}
    long_text = {}

    new_to_old = {}
    old_to_new = {}

    used_keys = set()

    for old_k, v in info.items():
        lk = old_k.lower()
        new_k = compress_key(old_k, used_keys)

        new_to_old[new_k] = old_k
        old_to_new[old_k] = new_k

        # ---- Long text ----
        if isinstance(v, str) and len(v) > 200:
            long_text[new_k] = v
            continue

        # ---- Date conversion ----
        if (
            isinstance(v, int)
            and v >= 1_000_000_000
            and any(x in lk for x in DATE_KEYS)
        ):
            if v > 1_000_000_000_000:
                v //= 1000
            try:
                main[new_k] = datetime.fromtimestamp(v, UTC).strftime("%d-%m-%Y")
            except:
                main[new_k] = v
            continue

        # ---- Large numbers (Cr/KCr/LCr) ----
        if isinstance(v, (int, float)) and abs(v) >= CR:
            av = abs(v)
            sign = -1 if v < 0 else 1

            if av >= LCR:
                main[new_k] = f"{sign * av / LCR:.2f} LCr"
            elif av >= KCR:
                main[new_k] = f"{sign * av / KCR:.2f} KCr"
            else:
                main[new_k] = f"{sign * av / CR:.2f} Cr"
            continue

        # ---- Float trimming ----
        if isinstance(v, float):
            main[new_k] = 0.0 if v == 0.0 else truncate(v)
            continue

        main[new_k] = v

    return main, long_text, new_to_old, old_to_new


# ======================================================
# NOISE
# ======================================================
NOISE_KEYS = {
    "maxAge", "priceHint", "triggerable",
    "customPriceAlertConfidence",
    "sourceInterval", "exchangeDataDelayedBy",
    "esgPopulated"
}

def is_noise(k):
    return k in NOISE_KEYS


# ======================================================
# DUPLICATE RESOLUTION (OLD KEYS)
# ======================================================
DUPLICATE_PRIORITY = {
    "price": ["regularMarketPrice", "currentPrice"],
    "prev": ["regularMarketPreviousClose", "previousClose"],
    "open": ["regularMarketOpen", "open"],
    "high": ["regularMarketDayHigh", "dayHigh"],
    "low": ["regularMarketDayLow", "dayLow"],
    "volume": ["regularMarketVolume", "volume"],
}

def resolve_duplicates(data, new_to_old):
    resolved = {}
    used_old = set()

    for keys in DUPLICATE_PRIORITY.values():
        for old_k in keys:
            for new_k, mapped_old in new_to_old.items():
                if mapped_old == old_k and new_k in data:
                    resolved[new_k] = data[new_k]
                    used_old.update(keys)
                    break
            else:
                continue
            break

    for new_k, v in data.items():
        if new_to_old[new_k] not in used_old:
            resolved[new_k] = v

    return resolved


# ======================================================
# CLASSIFIERS (UNCHANGED – OLD KEYS ONLY)
# ======================================================
def classify_price_volume_subgroup(old_key):
    k = old_key.lower()
    if "volume" in k: return "Volume"
    if "average" in k or "dma" in k: return "Moving Avg"
    if "week" in k or "beta" in k: return "Range / Vol"
    if "target" in k or "recommend" in k: return "Bid / Analyst"
    return "Live Price"


def classify_key(old_key, value):
    k = old_key.lower()

    if isinstance(value, (int, float)) and any(x in k for x in [
        "price", "volume", "avg", "change", "percent",
        "market", "week", "beta", "target"
    ]):
        return "price_volume"

    if any(x in k for x in [
        "revenue", "income", "profit", "margin",
        "pe", "pb", "roe", "roa", "debt", "equity"
    ]):
        return "fundamental"

    if isinstance(value, str) and len(value) > 80:
        return "long_text"

    return "profile"


# ======================================================
# GROUP BUILDER (KEY POINT)
# ======================================================
def build_grouped_info(info, new_to_old):
    groups = {
        "price_volume": {},
        "fundamental": {},
        "profile": {},
        "long_text": {},
    }

    for new_k, v in info.items():
        if v in [None, "", [], {}]:
            continue

        old_k = new_to_old.get(new_k, new_k)
        g = classify_key(old_k, v)
        groups[g][new_k] = v

    return groups


# ======================================================
# FORMATTERS
# ======================================================
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


def build_df_from_dict(data):
    rows = []
    for k, v in data.items():
        if is_noise(k):
            continue
        if isinstance(v, (int, float)):
            v = format_number(v)
        rows.append([k, v])
    return pd.DataFrame(rows, columns=["Field", "Value"])


# ======================================================
# MAIN ENTRY (CACHED)
# ======================================================
def fetch_info(symbol):
    cache_key = f"info_{symbol}"

    if exists(cache_key, "html"):
        cached = load(cache_key, "html")
        if cached:
            return cached

    try:
        raw = yfinfo(symbol)
        if not raw or "__error__" in raw:
            return "No data"

        info, long_text, new_to_old, _ = process_info(raw)
        groups = build_grouped_info(info, new_to_old)

        html = ""

        # ---- PRICE / VOLUME ----
        pv = resolve_duplicates(groups["price_volume"], new_to_old)
        for new_k, v in pv.items():
            html += f"<div><b>{new_k}</b> : {v}</div>"

        # ---- FUNDAMENTALS ----
        for new_k, v in groups["fundamental"].items():
            html += f"<div><b>{new_k}</b> : {v}</div>"

        # ---- PROFILE ----
        for new_k, v in groups["profile"].items():
            html += f"<div><b>{new_k}</b> : {v}</div>"

        # ---- LONG TEXT ----
        for v in long_text.values():
            html += f"<div style='margin-top:8px'>{v}</div>"

        save(cache_key, html, "html")
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"