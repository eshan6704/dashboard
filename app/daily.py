# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from . import persist
from .common import wrap_html

# ===========================================================
# RAW DAILY FETCHER
# ===========================================================
def daily(symbol, date_end, date_start):
    """Fetch daily OHLCV from Yahoo Finance."""
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    df = yf.download(symbol + ".NS", start=start, end=end)
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Remove column names / DataFrame name to avoid "Price" display
    df.columns.name = None
    df.index.name = None
    
    return df

# ===========================================================
# FETCH DAILY HTML TABLE
# ===========================================================
def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            print(f"[{date_end}] Using cached daily for {symbol}")
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df is None or df.empty:
            return wrap_html(f'<div id="daily_wrapper"><h1>No daily data for {symbol}</h1></div>')

        # Reset index if not simple RangeIndex
        if not isinstance(df.index, pd.RangeIndex):
            df.reset_index(inplace=True)

        # Convert numeric columns safely
        numeric_cols = ["Open","High","Low","Close","Adj Close","Volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with missing essential data
        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index(drop=True)

        # Format date
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            df = df.dropna(subset=["Date"]).reset_index(drop=True)
            df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")

        # Remove column name again just in case
        df.columns.name = None

        # Build HTML table WITHOUT any DataFrame name
        html_table = f'<div id="daily_table"><h2>{symbol} Daily Data</h2>{df.to_html(index=False, header=True, border=1, classes="daily-data", escape=False)}</div>'

        # Save to cache
        persist.save(key, html_table, "html")
        return html_table

    except Exception as e:
        return wrap_html(f'<div id="daily_wrapper"><h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre></div>')
