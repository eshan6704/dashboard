# stock.py  — compact, merged, single-file
from common import *
import yfinance as yf
import pandas as pd
import traceback
from ta_indi_pat import *
from persist import *

#file_name = f"bhav/bhav_{date_str.replace('-', '_')}.csv"
#upload_file("eshanhf",file_name,df)

# ================================================================
#                    BASIC YFINANCE FETCHERS
# ================================================================

def yfinfo(symbol):
    return yf.Ticker(symbol + ".NS").info

def qresult(symbol):
    
    return yf.Ticker(symbol + ".NS").quarterly_financials

def result(symbol):
    return yf.Ticker(symbol + ".NS").financials

def balance(symbol):
    return yf.Ticker(symbol + ".NS").balance_sheet

def cashflow(symbol):
    return yf.Ticker(symbol + ".NS").cashflow

def dividend(symbol):
    return yf.Ticker(symbol + ".NS").dividends.to_frame("Dividend")

def split(symbol):
    return yf.Ticker(symbol + ".NS").splits.to_frame("Split")

from datetime import datetime
import yfinance as yf

def intraday(symbol):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    return yf.download(symbol + ".NS", period="1d", interval="5m").round(2)


def daily(symbol):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    return yf.download(symbol + ".NS", period="1y", interval="1d").round(2)


# ================================================================
#              FETCH INFO  (USES COMMON.PY HELPERS)
# ================================================================

from common import (
    format_number,
    format_large_number,
    make_table,
    html_card,
    html_section,
    html_error,
    clean_df,
    safe_get,
    wrap_html
)

from chart_builder import build_chart
from ta_indi_pat import talib_df


def wrap_html(content, title="Market Data"):
    return f"<html><head><title>{title}</title></head><body>{content}</body></html>"

def make_table(df: pd.DataFrame):
    return df.to_html(index=False)
from datetime import datetime
import pandas as pd
import yfinance as yf

# Assumes save, load, exists, upload_file, wrap_html, make_table, intraday, daily, result, qresult,
# balance, cashflow, dividend, split, format_large_number, html_error are already defined

# -------------------------- INTRADAY ------------------------------
def fetch_intraday(symbol, indicators=None):
    key = f"intraday_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached intraday for {symbol}")
            return cached

    try:
        df = intraday(symbol)
        if df is False or df is None or df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Optional upload
        upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        # Preserve index in HTML
        df_display = df.tail(50).copy()
        df_display.reset_index(inplace=True)
        html = wrap_html(f"<h2>Last 50 Rows</h2>{make_table(df_display)}", title=f"{symbol} Intraday")

        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_intraday: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


# -------------------------- DAILY ------------------------------
def fetch_daily(symbol):
    key = f"daily_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached daily for {symbol}")
            return cached

    try:
        df = daily(symbol)
        if df is False or df is None or df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")

        upload_file("eshanhf", f"daily/{symbol}.csv", df)

        df_display = df.tail(50).copy()
        df_display.reset_index(inplace=True)
        html = wrap_html(f"<h2>Last 50 Rows</h2>{make_table(df_display)}", title=f"{symbol} Daily")

        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_daily: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


# -------------------------- QUARTERLY ------------------------------
def fetch_qresult(symbol):
    key = f"qresult_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached quarterly for {symbol}")
            return cached

    try:
        df = qresult(symbol)
        if df.empty:
            return wrap_html(f"<h1>No quarterly results for {symbol}</h1>")

        upload_file("eshanhf", f"qresult/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)  # preserve original index

        html = wrap_html(make_table(df_display), title=f"{symbol} Quarterly Results")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_qresult: {e}")
        return wrap_html(html_error(f"Quarterly Error: {e}"))


# -------------------------- ANNUAL ------------------------------
def fetch_result(symbol):
    key = f"result_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached annual for {symbol}")
            return cached

    try:
        df = result(symbol)
        if df.empty:
            return wrap_html(f"<h1>No annual results for {symbol}</h1>")

        upload_file("eshanhf", f"result/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Annual Results")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_result: {e}")
        return wrap_html(html_error(f"Annual Error: {e}"))


# -------------------------- BALANCE ------------------------------
def fetch_balance(symbol):
    key = f"balance_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached balance for {symbol}")
            return cached

    try:
        df = balance(symbol)
        if df.empty:
            return wrap_html(f"<h1>No balance sheet for {symbol}</h1>")

        upload_file("eshanhf", f"balance/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Balance Sheet")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_balance: {e}")
        return wrap_html(html_error(f"Balance Error: {e}"))


# -------------------------- CASHFLOW ------------------------------
def fetch_cashflow(symbol):
    key = f"cashflow_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached cashflow for {symbol}")
            return cached

    try:
        df = cashflow(symbol)
        if df.empty:
            return wrap_html(f"<h1>No cashflow for {symbol}</h1>")

        upload_file("eshanhf", f"cashflow/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Cash Flow")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_cashflow: {e}")
        return wrap_html(html_error(f"Cash Flow Error: {e}"))


# -------------------------- DIVIDEND ------------------------------
def fetch_dividend(symbol):
    key = f"dividend_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached dividend for {symbol}")
            return cached

    try:
        df = dividend(symbol)
        if df.empty:
            return wrap_html(f"<h1>No dividend history for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Dividends")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_dividend: {e}")
        return wrap_html(html_error(f"Dividend Error: {e}"))


# -------------------------- SPLIT ------------------------------
def fetch_split(symbol):
    key = f"split_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached split for {symbol}")
            return cached

    try:
        df = split(symbol)
        if df.empty:
            return wrap_html(f"<h1>No splits for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Splits")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_split: {e}")
        return wrap_html(html_error(f"Split Error: {e}"))


# -------------------------- OTHER (EARNINGS) ------------------------------
def fetch_other(symbol):
    key = f"other_{symbol}"
    if exists(key, "html"):
        cached = load(key, "html")
        if cached is not False:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached earnings for {symbol}")
            return cached

    try:
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.earnings
        if df.empty:
            return wrap_html(f"<h1>No earnings data for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if isinstance(x, (int, float)) else x)
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Earnings")
        save(key, html, "html")
        return html
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_other: {e}")
        return wrap_html(html_error(f"Earnings Error: {e}"))
