# stock.py — compact, merged, single-file (collision-safe)

import traceback
import pandas as pd
import yfinance as yf
from datetime import datetime as dt

# persist helpers
from . import persist
from .common import *
from . import backblaze as b2
#from . import ta_indi_pat



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



# ================================================================
#                         INTRADAY
# ================================================================

def fetch_intraday(symbol, indicators=None):
    key = f"intraday_{symbol}"



    try:
        df = intraday(symbol)
        if df is None or df is False or df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(
            f"<h2>Last 50 Rows</h2>{make_table(df_display)}",
            title=f"{symbol} Intraday"
        )


        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_intraday: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


# ================================================================
#                           DAILY
# ================================================================

# ================================================================
#                        QUARTERLY
# ================================================================

def fetch_qresult(symbol):
    key = f"qresult_{symbol}"


    try:
        df = qresult(symbol)
        if df.empty:
            return wrap_html(f"<h1>No quarterly results for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Quarterly Results")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_qresult: {e}")
        return wrap_html(html_error(f"Quarterly Error: {e}"))


# ================================================================
#                          ANNUAL
# ================================================================

def fetch_result(symbol):
    key = f"result_{symbol}"



    try:
        df = result(symbol)
        if df.empty:
            return wrap_html(f"<h1>No annual results for {symbol}</h1>")


        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Annual Results")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_result: {e}")
        return wrap_html(html_error(f"Annual Error: {e}"))


# ================================================================
#                        BALANCE SHEET
# ================================================================

def fetch_balance(symbol):
    key = f"balance_{symbol}"


    try:
        df = balance(symbol)
        if df.empty:
            return wrap_html(f"<h1>No balance sheet for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Balance Sheet")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_balance: {e}")
        return wrap_html(html_error(f"Balance Error: {e}"))


# ================================================================
#                          CASHFLOW
# ================================================================

def fetch_cashflow(symbol):
    key = f"cashflow_{symbol}"


    try:
        df = cashflow(symbol)
        if df.empty:
            return wrap_html(f"<h1>No cashflow for {symbol}</h1>")


        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Cash Flow")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_cashflow: {e}")
        return wrap_html(html_error(f"Cash Flow Error: {e}"))


# ================================================================
#                         DIVIDEND
# ================================================================

def fetch_dividend(symbol):
    key = f"dividend_{symbol}"


    try:
        df = dividend(symbol)
        if df.empty:
            return wrap_html(f"<h1>No dividend history for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Dividends")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_dividend: {e}")
        return wrap_html(html_error(f"Dividend Error: {e}"))


# ================================================================
#                            SPLIT
# ================================================================

def fetch_split(symbol):
    key = f"split_{symbol}"


    try:
        df = split(symbol)
        if df.empty:
            return wrap_html(f"<h1>No splits for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Splits")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_split: {e}")
        return wrap_html(html_error(f"Split Error: {e}"))


# ================================================================
#                           EARNINGS
# ================================================================

def fetch_other(symbol):
    key = f"other_{symbol}"


    try:
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.earnings

        if df.empty:
            return wrap_html(f"<h1>No earnings data for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)

        html = wrap_html(make_table(df_display), title=f"{symbol} Earnings")

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_other: {e}")
        return wrap_html(html_error(f"Earnings Error: {e}"))