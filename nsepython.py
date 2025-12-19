# ===============================================================
# Core imports (kept exactly as requested)
# ===============================================================
import os, sys, requests, pandas as pd, json, random, datetime, time, logging, re, urllib.parse
from collections import Counter


# ===============================================================
# Runtime mode
#   - "local": direct requests.Session
#   - "vpn"  : curl + cookie based access
# ===============================================================
mode = "local"


# ===============================================================
# NSE FETCH HANDLER
#   Single unified fetch function
#   Auto-handles cookies, headers, and retries
# ===============================================================

if mode == "vpn":

    def nsefetch(payload):
        """
        NSE fetch using curl + cookies (VPN-safe mode)
        """

        def encode(url):
            return url if "%26" in url or "%20" in url else urllib.parse.quote(url, safe=":/?&=")

        def refresh_cookies():
            os.popen(f'curl -c cookies.txt "https://www.nseindia.com" {curl_headers}').read()
            os.popen(f'curl -b cookies.txt -c cookies.txt "https://www.nseindia.com/option-chain" {curl_headers}').read()

        if not os.path.exists("cookies.txt"):
            refresh_cookies()

        encoded = encode(payload)
        cmd = f'curl -b cookies.txt "{encoded}" {curl_headers}'
        raw = os.popen(cmd).read()

        try:
            return json.loads(raw)
        except:
            refresh_cookies()
            raw = os.popen(cmd).read()
            try:
                return json.loads(raw)
            except:
                return {}

else:

    def nsefetch(payload):
        """
        NSE fetch using requests.Session (local / HF safe)
        """
        try:
            s = requests.Session()
            s.get("https://www.nseindia.com", headers=headers, timeout=10)
            s.get("https://www.nseindia.com/option-chain", headers=headers, timeout=10)
            return s.get(payload, headers=headers, timeout=10).json()
        except:
            return {}


# ===============================================================
# HTTP HEADERS
# ===============================================================

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

niftyindices_headers = {
    "Accept": "application/json,text/javascript,*/*;q=0.01",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://niftyindices.com",
    "Referer": "https://niftyindices.com/reports/historical-data",
    "User-Agent": "Mozilla/5.0"
}

curl_headers = '''
-H "authority: beta.nseindia.com"
-H "cache-control: max-age=0"
-H "user-agent: Mozilla/5.0"
-H "accept: */*"
--compressed
'''


# ===============================================================
# Runtime metadata
# ===============================================================
run_time = datetime.datetime.now()
indices = ["NIFTY", "FINNIFTY", "BANKNIFTY"]


# ===============================================================
# Helper utilities
# ===============================================================

def nsesymbolpurify(s):
    """Encode special NSE symbols"""
    return s.replace("&", "%26")


def flatten_dict(d, parent="", sep="."):
    """Flatten nested dictionaries"""
    items = {}
    for k, v in d.items():
        nk = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, nk, sep))
        else:
            items[nk] = v
    return items


def flatten_nested(d, prefix=""):
    """Flatten dicts + lists (deep NSE JSON support)"""
    flat = {}
    for k, v in d.items():
        nk = f"{prefix}{k}" if prefix == "" else f"{prefix}.{k}"
        if isinstance(v, dict):
            flat.update(flatten_nested(v, nk))
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                for i, x in enumerate(v):
                    flat.update(flatten_nested(x, f"{nk}.{i}"))
            else:
                flat[nk] = v
        else:
            flat[nk] = v
    return flat


def rename_col(cols):
    """Resolve duplicate column names after flattening"""
    child = [c.split(".")[-1] for c in cols]
    cnt = Counter(child)
    new = []
    for c, ch in zip(cols, child):
        if cnt[ch] == 1:
            new.append(ch)
        else:
            p = c.split(".")
            new.append(f"{p[-1]}_{p[-2]}" if len(p) >= 2 else p[-1])
    return new


def df_from_data(data):
    """Convert NSE JSON array into clean DataFrame"""
    rows = [flatten_nested(x) if isinstance(x, dict) else {"value": x} for x in data]
    df = pd.DataFrame(rows)
    df.columns = rename_col(df.columns)
    return df


# ===============================================================
# API WRAPPERS (No name changes)
# ===============================================================

def indices():
    p = nsefetch("https://www.nseindia.com/api/allIndices")
    return {
        "data": pd.DataFrame(p.pop("data")),
        "dates": pd.DataFrame([p.pop("dates")]),
        "indices": pd.DataFrame([p])
    }


def eq(symbol):
    symbol = nsesymbolpurify(symbol)
    df = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}")
    pre = df.pop("preOpenMarket")

    return {
        "securityInfo": pd.DataFrame([df["securityInfo"]]),
        "priceInfo": pd.DataFrame([flatten_dict(df["priceInfo"])]),
        "industryInfo": pd.DataFrame([df["industryInfo"]]),
        "pdSectorIndAll": pd.DataFrame([df["metadata"].pop("pdSectorIndAll")]),
        "metadata": pd.DataFrame([df["metadata"]]),
        "info": pd.DataFrame([df["info"]]),
        "preOpen": pd.DataFrame(pre.pop("preopen")),
        "preOpenMarket": pd.DataFrame([pre])
    }


def eq_fno():
    return nsefetch("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O")


def eq_der(symbol):
    return nsefetch("https://www.nseindia.com/api/quote-derivative?symbol=" + nsesymbolpurify(symbol))


def index_chain(symbol):
    return nsefetch("https://www.nseindia.com/api/option-chain-indices?symbol=" + nsesymbolpurify(symbol))


def eq_chain(symbol):
    return nsefetch("https://www.nseindia.com/api/option-chain-equities?symbol=" + nsesymbolpurify(symbol))


def nse_holidays(t="trading"):
    return nsefetch("https://www.nseindia.com/api/holiday-master?type=" + t)


def nse_results(index="equities", period="Quarterly"):
    if index in ["equities", "debt", "sme"] and period in ["Quarterly", "Annual", "Half-Yearly", "Others"]:
        return pd.json_normalize(
            nsefetch(f"https://www.nseindia.com/api/corporates-financial-results?index={index}&period={period}")
        )
    print("Invalid Input")


def nse_events():
    return pd.json_normalize(nsefetch("https://www.nseindia.com/api/event-calendar"))


def nse_past_results(symbol):
    return nsefetch("https://www.nseindia.com/api/results-comparision?symbol=" + nsesymbolpurify(symbol))


def nse_blockdeal():
    return nsefetch("https://nseindia.com/api/block-deal")


def nse_marketStatus():
    return nsefetch("https://nseindia.com/api/marketStatus")


def nse_circular(mode="latest"):
    return nsefetch(
        "https://www.nseindia.com/api/latest-circular"
        if mode == "latest"
        else "https://www.nseindia.com/api/circulars"
    )


def nse_fiidii(mode="pandas"):
    return pd.DataFrame(nsefetch("https://www.nseindia.com/api/fiidiiTradeReact"))


def nsetools_get_quote(symbol):
    p = nsefetch("https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O")
    for x in p["data"]:
        if x["symbol"] == symbol.upper():
            return x


def nse_index():
    p = nsefetch("https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json")
    return pd.DataFrame(p["data"])


# ===============================================================
# Historical / CSV endpoints
# ===============================================================

def nse_bhavcopy(d):
    return pd.read_csv(
        "https://archives.nseindia.com/products/content/sec_bhavdata_full_" + d.replace("-", "") + ".csv"
    )


def nse_highlow(d: str) -> pd.DataFrame:
    date_str = d.replace("-", "")
    url = f"https://archives.nseindia.com/content/CM_52_wk_High_low_{date_str}.csv"
    df = pd.read_csv(url, skiprows=2, engine="python")
    df.columns = df.columns.str.strip()
    return df


def nse_bulkdeals():
    return pd.read_csv("https://archives.nseindia.com/content/equities/bulk.csv")


def nse_blockdeals():
    return pd.read_csv("https://archives.nseindia.com/content/equities/block.csv")
