import requests
import pandas as pd

# ======================================================
# Base Headers (mandatory for NSE API)
# ======================================================
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


# ======================================================
# Helper: Convert DataFrame to HTML (single block)
# ======================================================
def _to_html(title, df):
    if df is None or len(df) == 0:
        return f"<h3>{title}</h3><p>No data available</p>"
    return f"<h3>{title}</h3>" + df.to_html(index=False, border=1)


# ======================================================================
# STOCK QUOTE (similar to get_quote)
# ======================================================================
def nse_stock(symbol):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol.upper()}"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        info = pd.json_normalize(data.get("info", {}))
        price = pd.json_normalize(data.get("priceInfo", {}))
        meta = pd.json_normalize(data.get("metadata", {}))

        html = ""
        html += _to_html("Stock Info", info)
        html += _to_html("Price Info", price)
        html += _to_html("Metadata", meta)

        return html

    except Exception as e:
        return f"<p>Error fetching stock: {e}</p>"


# ======================================================================
# OPTION CHAIN (similar to get_option_chain)
# ======================================================================
def nse_fno(symbol):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol.upper()}"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        records = data.get("records", {})

        all_data = pd.DataFrame(records.get("data", []))
        ce_list = [x["CE"] for x in records.get("data", []) if "CE" in x]
        pe_list = [x["PE"] for x in records.get("data", []) if "PE" in x]

        df_ce = pd.DataFrame(ce_list)
        df_pe = pd.DataFrame(pe_list)

        html = ""
        html += _to_html("F&O Combined", all_data)
        html += _to_html("CALL Options (CE)", df_ce)
        html += _to_html("PUT Options (PE)", df_pe)

        return html

    except Exception as e:
        return f"<p>Error fetching FNO: {e}</p>"


# ======================================================================
# FUTURES DATA
# ======================================================================
def nse_future(symbol):
    url = f"https://www.nseindia.com/api/quote-derivative?symbol={symbol.upper()}"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        futures = pd.DataFrame(data.get("stocks", []))
        meta = pd.json_normalize(data.get("info", {}))

        html = ""
        html += _to_html("Futures Data", futures)
        html += _to_html("Metadata", meta)

        return html

    except Exception as e:
        return f"<p>Error fetching futures: {e}</p>"


# ======================================================================
# 52-WEEK HIGH / LOW
# ======================================================================
def nse_high_low():
    url = "https://www.nseindia.com/api/market-data-52Week"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        high = pd.DataFrame(data.get("FiftyTwoWeekHigh", []))
        low = pd.DataFrame(data.get("FiftyTwoWeekLow", []))

        html = ""
        html += _to_html("52 Week High", high)
        html += _to_html("52 Week Low", low)

        return html

    except Exception as e:
        return f"<p>Error fetching high-low: {e}</p>"


# ======================================================================
# BHAVCOPY
# ======================================================================
def nse_bhav(date_str):
    """
    Supports input date format:
    - DDMMYYYY
    - DD-MM-YYYY
    - DD/MM/YYYY
    Converts automatically to DDMMYYYY for NSE API.
    """

    # ---------------------------
    # Normalize date
    # ---------------------------
    try:
        # Replace "-" or "/" with ""
        clean = date_str.replace("-", "").replace("/", "")

        # Now clean should be DDMMYYYY
        if len(clean) != 8:
            return "<p>Error: Invalid date format. Use DDMMYYYY / DD-MM-YYYY / DD/MM/YYYY</p>"

        # Final API format = DDMMYYYY
        api_date = clean

    except Exception:
        return "<p>Error: Unable to parse date.</p>"

    # ---------------------------
    # Fetch Data
    # ---------------------------
    url = (
        "https://www.nseindia.com/api/reports"
        f"?archives=true&date={api_date}&type=equities&mode=single"
    )

    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        df = pd.DataFrame(data.get("data", []))

        return _to_html(f"Bhavcopy {api_date}", df)

    except Exception as e:
        return f"<p>Error fetching bhavcopy: {e}</p>"


# ======================================================================
# ALL NSE INDICES LIST
# ======================================================================
def nse_indices():
    url = "https://www.nseindia.com/api/allIndices"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        df = pd.DataFrame(data.get("data", []))

        return _to_html("All NSE Indices", df)

    except Exception as e:
        return f"<p>Error fetching indices: {e}</p>"


# ======================================================================
# NSE OPEN MARKET DATA (same endpoint used in nsepython)
# ======================================================================
def nse_open(index_name):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        meta = pd.json_normalize(data.get("metadata", {}))
        df = pd.DataFrame(data.get("data", []))

        html = ""
        html += _to_html("Index Metadata", meta)
        html += _to_html("Index Open Data", df)

        return html

    except Exception as e:
        return f"<p>Error fetching open data: {e}</p>"


# ======================================================================
# NSE PRE-OPEN MARKET DATA
# ======================================================================
def nse_preopen(index_name):
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"
    try:
        r = requests.get(url, headers=NSE_HEADERS)
        data = r.json()

        df = pd.DataFrame(data.get("data", []))
        meta = pd.json_normalize(data.get("metadata", {}))

        html = ""
        html += _to_html("Pre-Open Metadata", meta)
        html += _to_html("Pre-Open Market Data", df)

        return html

    except Exception as e:
        return f"<p>Error fetching preopen: {e}</p>"
