# stock.py — compact, merged, single-file (collision-safe)

import traceback
import pandas as pd
import yfinance as yf
from datetime import datetime as dt

# persist helpers
from . import persist
from .common import *
from . import backblaze as b2
from . import ta_indi_pat



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


def intraday(symbol):
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    return yf.download(symbol + ".NS", period="1d", interval="5m").round(2)


def daily2(symbol,date_end,date_start):
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    return yf.download(symbol + ".NS", start=start,end=end).round(2)



# ================================================================
#                         INTRADAY
# ================================================================

def fetch_intraday(symbol, indicators=None,b2_save=False):
    key = f"intraday_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached intraday for {symbol}")
            return cached

    try:
        df = intraday(symbol)
        if df is None or df is False or df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(
            f"<h2>Last 50 Rows</h2>{make_table(df_display)}",
            title=f"{symbol} Intraday"
        )

        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_intraday: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


# ================================================================
#                           DAILY
# ================================================================

def fetch_daily2(symbol,date_end,date_start,b2_save=False):
    key = f"daily_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{date_end}] Using cached daily for {symbol}")
            return cached

    try:
        df = daily(symbol,date_end,date_start)
        if df is None or df is False or df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(
            f"<h2>Last 50 Rows</h2>{make_table(df_display)}",
            title=f"{symbol} Daily"
        )

        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_daily: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


# ================================================================
#                        QUARTERLY
# ================================================================

def fetch_qresult(symbol,b2_save=False):
    key = f"qresult_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached quarterly for {symbol}")
            return cached

    try:
        df = qresult(symbol)
        if df.empty:
            return wrap_html(f"<h1>No quarterly results for {symbol}</h1>")

        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Quarterly Results")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_qresult: {e}")
        return wrap_html(html_error(f"Quarterly Error: {e}"))


# ================================================================
#                          ANNUAL
# ================================================================

def fetch_result(symbol,b2_save=False):
    key = f"result_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached annual for {symbol}")
            return cached

    try:
        df = result(symbol)
        if df.empty:
            return wrap_html(f"<h1>No annual results for {symbol}</h1>")

        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Annual Results")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_result: {e}")
        return wrap_html(html_error(f"Annual Error: {e}"))


# ================================================================
#                        BALANCE SHEET
# ================================================================

def fetch_balance(symbol,b2_save=False):
    key = f"balance_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached balance for {symbol}")
            return cached

    try:
        df = balance(symbol)
        if df.empty:
            return wrap_html(f"<h1>No balance sheet for {symbol}</h1>")

        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Balance Sheet")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_balance: {e}")
        return wrap_html(html_error(f"Balance Error: {e}"))


# ================================================================
#                          CASHFLOW
# ================================================================

def fetch_cashflow(symbol,b2_save=False):
    key = f"cashflow_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached cashflow for {symbol}")
            return cached

    try:
        df = cashflow(symbol)
        if df.empty:
            return wrap_html(f"<h1>No cashflow for {symbol}</h1>")

        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Cash Flow")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_cashflow: {e}")
        return wrap_html(html_error(f"Cash Flow Error: {e}"))


# ================================================================
#                         DIVIDEND
# ================================================================

def fetch_dividend(symbol,b2_save=False):
    key = f"dividend_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached dividend for {symbol}")
            return cached

    try:
        df = dividend(symbol)
        if df.empty:
            return wrap_html(f"<h1>No dividend history for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)
        html = wrap_html(make_table(df_display), title=f"{symbol} Dividends")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_dividend: {e}")
        return wrap_html(html_error(f"Dividend Error: {e}"))


# ================================================================
#                            SPLIT
# ================================================================

def fetch_split(symbol,b2_save=False):
    key = f"split_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached split for {symbol}")
            return cached

    try:
        df = split(symbol)
        if df.empty:
            return wrap_html(f"<h1>No splits for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)
        html = wrap_html(make_table(df_display), title=f"{symbol} Splits")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_split: {e}")
        return wrap_html(html_error(f"Split Error: {e}"))


# ================================================================
#                           EARNINGS
# ================================================================

def fetch_other(symbol,b2_save=False):
    key = f"other_{symbol}"

    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached is not False:
            print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Using cached earnings for {symbol}")
            return cached

    try:
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.earnings

        if df.empty:
            return wrap_html(f"<h1>No earnings data for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        if b2_save:
            b2.upload_file("eshanhf", f"intraday/{symbol}.csv", df)
        html = wrap_html(make_table(df_display), title=f"{symbol} Earnings")
        persist.save(key, html, "html")
        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_other: {e}")
        return wrap_html(html_error(f"Earnings Error: {e}"))