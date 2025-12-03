# ================================
# NSE Fetch Module (DF Only)
# ================================

import datetime
import pandas as pd
import time
import requests
import nsepython # Moved import here
#import nse
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

# ---------------------------------------------------
# Helper: JSON Fetch
# ---------------------------------------------------
def fetch_data(url):
    try:
        response = session.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None

# ---------------------------------------------------
# Clean DF
# ---------------------------------------------------
def clean_dataframe(df):
    df.columns = df.columns.str.strip()
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
    df.fillna(0.01, inplace=True)
    return df

# ---------------------------------------------------
# Bhavcopy Fetch → DataFrame
# ---------------------------------------------------
def fetch_bhavcopy_df(date):
    """Returns Cleaned Bhavcopy DF for EQ / BE / SM"""
    date_str = date.strftime("%d-%m-%Y")
    print(f"Attempting to fetch bhavcopy for date: {date_str}")

    try:
        df = nsepython.get_bhavcopy(date_str) # Direct call
        if df is None or df.empty:
            print(f"No bhavcopy data or empty DataFrame returned for {date_str}")
            return None, None

        actual_bhavcopy_date = datetime.datetime.strptime(
            df.iloc[2, 2].strip(), "%d-%b-%Y"
        ).date()

        df = clean_dataframe(df)
        df_filtered = df[df.iloc[:, 1].isin(["EQ", "BE", "SM"])]

        return df_filtered, actual_bhavcopy_date

    except Exception as e:
        print(f"An error occurred while fetching bhavcopy for {date_str}: {e}")
        return None, None

# ---------------------------------------------------
# Stock Deliverable DF (security-wise archive)
# ---------------------------------------------------
def fetch_stock_df(nse_module, stock, start, end, series="ALL"):
    """Return DF for security-wise archive (deliverable + all columns)"""

    df = nse_module.security_wise_archive(start, end, stock, series)
    if df is not None and not df.empty:
        return df
    return None

# ---------------------------------------------------
# All NSE Indices → DataFrames
# ---------------------------------------------------
def indices():
    url = "https://www.nseindia.com/api/allIndices"
    data = fetch_data(url)
    if data is None:
        return None

    # DataFrames
    df_dates = pd.DataFrame([data["dates"]])
    df_meta = pd.DataFrame([{k: v for k, v in data.items() if k not in ["data", "dates"]}])
    df_data = pd.DataFrame(data["data"])

    # Convert to HTML pieces
    html_dates = df_dates.to_html(index=False, border=1)
    html_meta  = df_meta.to_html(index=False, border=1)
    html_data  = df_data.to_html(index=False, border=1)

    # Combine into one single HTML block
    full_html = (
        "<h3>Dates</h3>" + html_dates +
        "<br><h3>Meta</h3>" + html_meta +
        "<br><h3>Data</h3>" + html_data
    )

    return full_html

# ---------------------------------------------------
# Specific Index → DataFrames
# ---------------------------------------------------
'''
def open(index_name="NIFTY 50"):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    data = fetch_data(url)
    if data is None:
        return None

    # Create DataFrames
    df_market = pd.DataFrame([data["marketStatus"]])
    df_adv    = pd.DataFrame([data["advance"]])
    df_meta   = pd.DataFrame([data["metadata"]])
    df_data   = pd.DataFrame(data["data"])

    # Convert to HTML
    html_market = df_market.to_html(index=False, border=1)
    html_adv    = df_adv.to_html(index=False, border=1)
    html_meta   = df_meta.to_html(index=False, border=1)
    html_data   = df_data.to_html(index=False, border=1)

    # Combine all into single HTML string
    full_html = (
        "<h3>Market Status</h3>" + html_market +
        "<br><h3>Advance / Decline</h3>" + html_adv +
        "<br><h3>Metadata</h3>" + html_meta +
        "<br><h3>Index Data</h3>" + html_data
    )

    return full_html

'''
def open(index_name="NIFTY 50"):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    data = fetch_data(url)

    if data is None:
        return "<h3>No Data</h3>"

    # Extract base parts
    df_market = pd.DataFrame([data["marketStatus"]])
    df_adv    = pd.DataFrame([data["advance"]])
    df_data   = pd.DataFrame(data["data"])

    # ------------------------------
    # Merge child meta keys into df_data
    # ------------------------------
    def flatten_meta(row):
        meta = row.get("meta", {})
        flat = {}
        for k, v in meta.items():
            if isinstance(v, dict):  # flatten one level
                for ck, cv in v.items():
                    flat[f"{k}_{ck}"] = cv
            else:
                flat[k] = v
        return pd.Series(flat)

    # Expand meta into columns
    df_meta_expanded = df_data.apply(flatten_meta, axis=1)

    # Merge expanded meta into df_data
    df_data = pd.concat([df_data.drop(columns=["meta"], errors="ignore"),
                         df_meta_expanded], axis=1)

    # ------------------------------
    # Convert to HTML
    # ------------------------------
    html_market = df_market.to_html(index=False, border=1)
    html_adv    = df_adv.to_html(index=False, border=1)
    html_data   = df_data.to_html(index=False, border=1)

    full_html = (
        "<h3>Market Status</h3>" + html_market +
        "<br><h3>Advance/Decline</h3>" + html_adv +
        "<br><h3>Index Data (with META merged)</h3>" + html_data
    )

    return full_html

# ---------------------------------------------------
# Option Chain DF (Raw CE/PE)
# ---------------------------------------------------
def fetch_option_chain_df(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    data = fetch_data(url)

    if data and "filtered" in data:
        ce_df = pd.DataFrame([r["CE"] for r in data["filtered"]["data"] if "CE" in r])
        pe_df = pd.DataFrame([r["PE"] for r in data["filtered"]["data"] if "PE" in r])
        return ce_df, pe_df

    return None, None

# ---------------------------------------------------
# Pre-open market → DataFrame
# ---------------------------------------------------
def preopen(key="NIFTY"):
    url = f"https://www.nseindia.com/api/market-data-pre-open?key={key}"
    data = fetch_data(url)
    if not data:
        return None

    df = pd.DataFrame(data.get("data", []))

    # Convert to one HTML table
    html_table = df.to_html(index=False, border=1)

    # Wrap into single block
    full_html = "<h3>Pre-Open Market Data</h3>" + html_table

    return full_html

# ---------------------------------------------------
# FNO Quote → DataFrames
# ---------------------------------------------------
def fno(symbol):
    payload = nsepython.nse_quote(symbol)
    if not payload:
        return None

    # ---------- INFO ----------
    info_keys = list(payload["info"].keys()) + [
        "fut_timestamp",
        "opt_timestamp",
        "maxVolatility",
        "minVolatility",
        "avgVolatility",
    ]

    info_values = list(payload["info"].values()) + [
        payload["fut_timestamp"],
        payload["opt_timestamp"],
        payload["underlyingInfo"]["volatility"][0]['maxVolatility'],
        payload["underlyingInfo"]["volatility"][0]['minVolatility'],
        payload["underlyingInfo"]["volatility"][0]['avgVolatility'],
    ]

    df_info = pd.DataFrame([info_values], columns=info_keys)

    # ---------- MCAP ----------
    df_mcap = pd.DataFrame(payload["underlyingInfo"].get("marketCap", {}))

    # ---------- FNO LIST ----------
    df_fno_list = pd.DataFrame(payload.get("allSymbol", []), columns=["FNO_Symbol"])

    # ---------- STOCK DEPTH ----------
    df_stock = process_stocks_df(payload["stocks"])

    # Convert all to HTML
    html_info = df_info.to_html(index=False, border=1)
    html_mcap = df_mcap.to_html(index=False, border=1)
    html_fno  = df_fno_list.to_html(index=False, border=1)
    html_stock = df_stock.to_html(index=False, border=1)

    # Combine into full HTML block
    full_html = (
        "<h3>FNO Info</h3>" + html_info +
        "<br><h3>Market Cap</h3>" + html_mcap +
        "<br><h3>FNO Symbol List</h3>" + html_fno +
        "<br><h3>Stock Depth</h3>" + html_stock
    )

    return full_html

# ---------------------------------------------------
# Handle nested stock → DF
# ---------------------------------------------------
def process_stocks_df(data):
    """Return final merged stock DF only"""
    trade_info_list, other_info_list = [], []
    bid_ask_list = []
    stock_values = []
    trade_keys = other_keys = bidask_keys = stock_keys = None

    for i, stock in enumerate(data):
        meta = stock.pop("metadata")
        depth = stock.pop("marketDeptOrderBook")
        parent = stock

        trade_info = depth.pop("tradeInfo", {})
        other_info = depth.pop("otherInfo", {})

        trade_info_list.append(trade_info)
        other_info_list.append(other_info)

        # bid / ask
        bid_ask_row = {}
        for side in ["bid", "ask"]:
            for j, entry in enumerate(depth.get(side, []), start=1):
                bid_ask_row[f"{side}_price_{j}"] = entry.get("price")
                bid_ask_row[f"{side}_qty_{j}"] = entry.get("quantity")

        bid_ask_list.append(bid_ask_row)

        if i == 0:
            trade_keys = list(trade_info.keys())
            other_keys = list(other_info.keys())
            bidask_keys = list(bid_ask_row.keys())
            stock_keys = list(meta.keys()) + list(depth.keys()) + list(parent.keys())

        stock_values.append(
            list(meta.values()) + list(depth.values()) + list(parent.values())
        )

    df_trade = pd.DataFrame(trade_info_list, columns=trade_keys)
    df_other = pd.DataFrame(other_info_list, columns=other_keys)
    df_bidask = pd.DataFrame(bid_ask_list, columns=bidask_keys)
    df_stock = pd.DataFrame(stock_values, columns=stock_keys)

    df_stock = df_stock.drop(columns=['bid', 'ask', 'carryOfCost'], errors="ignore")

    return pd.concat([df_stock, df_trade, df_other, df_bidask], axis=1)




#date = datetime.date(2025, 11, 27) # Trying a past date where data is likely available

#df = nse_preopen_df("NIFTY")
#df_bhav, act_date = fetch_bhavcopy_df(date)
#df_ce, df_pe = fetch_option_chain_df("NIFTY")
#df_m, df_a, df_meta, df_data = nse_index_df("NIFTY 50")

#fno = nse_fno_df("RELIANCE")


# -----------------------------
# Global Variables
# -----------------------------
nse_del_key_map = {
    'Symbol': "Symbol", 'Series': "Series",
    'Date': 'Date', 'Prev Close': 'Preclose',
    'Open Price': 'Open', 'High Price': 'High',
    'Low Price': 'Low', 'Last Price': 'Last',
    'Close Price': 'Close', 'Average Price': 'AvgPrice',
    'Total Traded Quantity': 'Volume',
    'Turnover ₹': 'Turnover', 'No. of Trades': "Trades",
    'Deliverable Qty': "Delivery", '% Dly Qt to Traded Qty': "Del%"
}

# -----------------------------
# Data Fetching Functions (NSE)
# -----------------------------
def url_nse_del(symbol, start_date, end_date):
    base_url = "https://www.nseindia.com/api/historicalOR/generateSecurityWiseHistoricalData"
    start_date_str = start_date.strftime("%d-%m-%Y")
    end_date_str = end_date.strftime("%d-%m-%Y")
    url = f"{base_url}?from={start_date_str}&to={end_date_str}&symbol={symbol.split('.')[0]}&type=priceVolumeDeliverable&series=ALL&csv=true"
    return url

def to_numeric_safe(series):
    series = series.replace('-', 0)
    series = series.fillna(0)
    series = series.astype(str).str.replace(',', '')
    return pd.to_numeric(series, errors='coerce').fillna(0)

def nse_daily(symbol, start_date_str=None, end_date_str=None):
    # Default end date is today
    end_date = datetime.now()
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Warning: Invalid end date format '{end_date_str}'. Using today's date.")
            end_date = datetime.now()

    # Default start date is one year prior
    start_date = end_date - timedelta(days=365)
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Warning: Invalid start date format '{start_date_str}'. Using default start date.")
            start_date = end_date - timedelta(days=365)

    # Swap if needed
    if start_date > end_date:
        print("Warning: Start date is after end date. Swapping dates.")
        start_date, end_date = end_date, start_date

    url = url_nse_del(symbol, start_date, end_date)
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if not response.content:
            return None

        # Build DataFrame
        df = pd.read_csv(io.StringIO(response.content.decode("utf-8"))).round(2)
        df.columns = df.columns.str.strip()
        df.rename(columns=nse_del_key_map, inplace=True)

        # Capitalize column names
        df.columns = [col.capitalize() for col in df.columns]

        # Remove unwanted columns
        df.drop(columns=["Symbol", "Series", "Avgprice", "Last"], errors="ignore", inplace=True)

        # Format date
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y").dt.strftime("%Y-%m-%d")

        # Ensure numeric columns
        numeric_cols = ['Close', 'Preclose', 'Open', 'High', 'Low', 'Volume', 'Delivery', 'Turnover', 'Trades']
        numeric_cols_cap = [c.capitalize() for c in numeric_cols]

        for col in numeric_cols_cap:
            if col in df.columns:
                df[col] = to_numeric_safe(df[col])
            else:
                df[col] = 0

        # Convert to HTML
        html_table = df.to_html(index=False, border=1)

        full_html = "<h3>Daily Data</h3>" + html_table
        return full_html

    except Exception as e:
        print(f"Error fetching data from NSE for {symbol}: {e}")
        return None

