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
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    df = yf.download(symbol + ".NS", start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df.index.name = None
    return df

# ===========================================================
# DAILY TABLE GENERATOR
# ===========================================================
def fetch_daily(symbol, date_end, date_start):
    """Return HTML table of daily stock data."""
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")

        # Ensure numeric columns
        for col in ["Open","High","Low","Close","Adj Close","Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index(drop=True)

        # Ensure Date column
        df["Date"] = pd.to_datetime(df.index if "Date" not in df.columns else df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")

        # Safe Adj Close
        if "Adj Close" not in df.columns:
            df["Adj Close"] = ""

        # Daily change %
        df["Change %"] = ((df["Close"] - df["Open"]) / df["Open"] * 100).round(2)

        # Build HTML table
        html_table = f'<div id="daily_dashboard" style="max-height:600px; overflow:auto; font-family:Arial,sans-serif;">'
        html_table += '<table border="1" style="border-collapse:collapse; width:100%;">'
        html_table += '<thead style="position:sticky; top:0; background:#1a4f8a; color:white;">'
        html_table += '<tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Adj Close</th><th>Volume</th><th>Change %</th></tr>'
        html_table += '</thead><tbody>'

        for idx, r in df.iterrows():
            row_color = "#e8f5e9" if idx % 2 == 0 else "#f5f5f5"
            change_color = "green" if r["Change %"] > 0 else "red" if r["Change %"] < 0 else "black"

            html_table += f'<tr style="background:{row_color};">'
            html_table += f'<td>{r["Date"]}</td>'
            html_table += f'<td>{r["Open"]}</td>'
            html_table += f'<td>{r["High"]}</td>'
            html_table += f'<td>{r["Low"]}</td>'
            html_table += f'<td>{r["Close"]}</td>'
            html_table += f'<td>{r["Adj Close"]}</td>'
            html_table += f'<td>{r["Volume"]}</td>'
            html_table += f'<td style="color:{change_color}; font-weight:600;">{r["Change %"]}%</td>'
            html_table += '</tr>'

        html_table += '</tbody></table></div>'

        persist.save(key, html_table, "html")
        return html_table

    except Exception as e:
        return wrap_html(f"<h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre>")
