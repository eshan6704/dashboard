import yfinance as yf
import pandas as pd
import io
import requests

from datetime import datetime, timedelta
from ta_indi_pat import talib_df  # use the combined talib_df function
from common import html_card, wrap_html

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


def nse_del(symbol, start_date_str=None, end_date_str=None):
    # Default end date is today
    end_date = datetime.now()
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Warning: Invalid end date format '{end_date_str}'. Using today's date.")
            end_date = datetime.now()

    # Default start date is one year prior to end_date
    start_date = end_date - timedelta(days=365)
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Warning: Invalid start date format '{start_date_str}'. Using default start date.")
            start_date = end_date - timedelta(days=365)

    # Ensure start_date is not after end_date
    if start_date > end_date:
        print("Warning: Start date is after end date. Swapping dates.")
        start_date, end_date = end_date, start_date

    url = url_nse_del(symbol, start_date, end_date)
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.content:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8'))).round(2)
            df.columns = df.columns.str.strip()
            df.rename(columns=nse_del_key_map, inplace=True)

            # Capitalize the first letter of ALL column names after renaming
            df.columns = [col.capitalize() for col in df.columns]

            # Remove 'Symbol', 'Series', 'Avgprice', and 'Last' columns (now capitalized)
            df.drop(columns=['Symbol','Series','Avgprice','Last'], errors='ignore', inplace=True)

            # Convert 'Date' column to datetime objects
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y').dt.strftime('%Y-%m-%d')

            numeric_cols = ['Close', 'Preclose', 'Open', 'High', 'Low', 'Volume', 'Delivery', 'Turnover', 'Trades']
            # Ensure numeric_cols are capitalized before checking and conversion
            numeric_cols_capitalized = [col.capitalize() for col in numeric_cols]
            for col in numeric_cols_capitalized:
                if col in df.columns:
                    df[col] = to_numeric_safe(df[col])
                else:
                    df[col] = 0
            return df
    except Exception as e:
        print(f"Error fetching data from NSE for {symbol}: {e}")
    return None

def daily(symbol,source="yfinace"):
    if source=="yfinance":
        df = yf.download(symbol + ".NS", period="1y", interval="1d").round(2)
        if df.empty:
            return html_card("Error", f"No daily data found for {symbol}")

        # --- Standardize columns ---
        df.columns = ["Close", "High", "Low", "Open", "Volume"]
        df.reset_index(inplace=True)  # make Date a column
    
    if source=="NSE":
        df=nse_del(symbol)
    return df
def fetch_daily(symbol, source,max_rows=200):
    """
    Fetch daily OHLCV data, calculate TA-Lib indicators + patterns,
    return a single scrollable HTML table.
    """
    try:
        # --- Fetch daily data ---
        df=daily(symbol,source)

        # --- Limit rows for display ---
        df_display = df.head(max_rows)

        # --- Generate combined TA-Lib DataFrame ---
        combined_df = talib_df(df_display)

        # --- Convert to HTML table ---
        table_html = combined_df.to_html(
            classes="table table-striped table-bordered",
            index=False
        )

        # --- Wrap in scrollable div ---
        scrollable_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:600px; border:1px solid #ccc; padding:5px;">
            {table_html}
        </div>
        """

        # --- Wrap in card and full HTML ---
        content = f"""
        <h2>{symbol} - Daily Data (OHLCV + Indicators + Patterns)</h2>
        {html_card("TA-Lib Data", scrollable_html)}
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
