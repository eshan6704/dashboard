# stock.py  — compact, merged, single-file
from common import *
import yfinance as yf
import pandas as pd
import traceback
from ta_indi_pat import *

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

def intraday(symbol):
    return yf.download(symbol + ".NS", period="1d", interval="5m").round(2)

def daily(symbol):
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


# -------------------------- INTRADAY ------------------------------

def fetch_intraday(symbol, indicators=None):
    try:
        df = intraday(symbol)
        if df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        file_name = f"intraday/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        #chart_html = build_chart(df, indicators=indicators)
        table_html = make_table(df.tail(50))
        return wrap_html(f"<h2>Last 50 Rows</h2>{table_html}",
                         title=f"{symbol} Intraday")

    except Exception as e:
        return wrap_html(f"<h1>Error:{e}</h1>")


# -------------------------- DAILY ------------------------------

def fetch_daily(symbol, source="yfinance", max_rows=200):
    try:
        df = daily(symbol)
        

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        file_name = f"daily/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        df_disp = df.head(max_rows)   
        combined_df = talib_df(df_disp)
        table_html = combined_df.to_html(
            classes="table table-striped table-bordered",
            index=False
        )

        scroll = f"""
        <div style="overflow:auto; max-height:600px; border:1px solid #ccc;">
            {table_html}
        </div>
        """

        return wrap_html(f"<h2>{symbol} Daily</h2>" + html_card("TA-Lib", scroll))

    except Exception as e:
        return html_card("Error", str(e))


# -------------------------- QUARTERLY ------------------------------

def fetch_qresult(symbol):
    try:
        df = qresult(symbol)
        if df.empty:
            return wrap_html(f"<h1>No quarterly results for {symbol}</h1>")
        file_name = f"qresult/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Quarterly Results")

    except Exception as e:
        return wrap_html(html_error(f"Quarterly Error: {e}"))


# -------------------------- ANNUAL ------------------------------

def fetch_result(symbol):
    try:
        df = result(symbol)
        if df.empty:
            return wrap_html(f"<h1>No annual results for {symbol}</h1>")
        file_name = f"result/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Annual Results")

    except Exception as e:
        return wrap_html(html_error(f"Annual Error: {e}"))


# -------------------------- BALANCE ------------------------------

def fetch_balance(symbol):
    try:
        df = balance(symbol)
        if df.empty:
            return wrap_html(f"<h1>No balance sheet for {symbol}</h1>")
        file_name = f"balance/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Balance Sheet")

    except Exception as e:
        return wrap_html(html_error(f"Balance Error: {e}"))


# -------------------------- CASHFLOW ------------------------------

def fetch_cashflow(symbol):
    try:
        df = cashflow(symbol)
        if df.empty:
            return wrap_html(f"<h1>No cashflow for {symbol}</h1>")
        file_name = f"cashflow/{symbol}_{date_str.replace('-', '_')}.csv"
        upload_file("eshanhf",file_name,df)
        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Cash Flow")

    except Exception as e:
        return wrap_html(html_error(f"Cash Flow Error: {e}"))


# -------------------------- DIVIDEND ------------------------------

def fetch_dividend(symbol):
    try:
        df = dividend(symbol)
        if df.empty:
            return wrap_html(f"<h1>No dividend history for {symbol}</h1>")

        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Dividends")

    except Exception as e:
        return wrap_html(html_error(f"Dividend Error: {e}"))


# -------------------------- SPLIT ------------------------------

def fetch_split(symbol):
    try:
        df = split(symbol)
        if df.empty:
            return wrap_html(f"<h1>No splits for {symbol}</h1>")

        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )
        df_fmt.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_fmt.index]

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Splits")

    except Exception as e:
        return wrap_html(html_error(f"Split Error: {e}"))


# -------------------------- OTHER (EARNINGS) ------------------------------

def fetch_other(symbol):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        df = ticker.earnings

        if df.empty:
            return wrap_html(f"<h1>No earnings data for {symbol}</h1>")

        df_fmt = df.copy()
        for col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        return wrap_html(make_table(df_fmt),
                         title=f"{symbol} Earnings")

    except Exception as e:
        return wrap_html(html_error(f"Earnings Error: {e}"))
