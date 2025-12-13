# stock.py  — compact, merged, single-file

import yfinance as yf
import pandas as pd
import traceback

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


# -------------------------- INFO ------------------------------

def fetch_info2(symbol):
    try:
        info = yfinfo(symbol)
        if not info:
            return html_error(f"No information found for {symbol}")

        basic = {
            "Symbol": symbol,
            "Name": safe_get(info, "longName"),
            "Sector": safe_get(info, "sector"),
            "Industry": safe_get(info, "industry"),
            "Website": safe_get(info, "website"),
            "Employee Count": format_large_number(safe_get(info, "fullTimeEmployees")),
        }
        df_basic = pd.DataFrame(basic.items(), columns=["Field", "Value"])

        price_info = {
            "Current Price": format_number(safe_get(info, "currentPrice")),
            "Previous Close": format_number(safe_get(info, "previousClose")),
            "Open": format_number(safe_get(info, "open")),
            "Day High": format_number(safe_get(info, "dayHigh")),
            "Day Low": format_number(safe_get(info, "dayLow")),
            "52W High": format_number(safe_get(info, "fiftyTwoWeekHigh")),
            "52W Low": format_number(safe_get(info, "fiftyTwoWeekLow")),
            "Volume": format_large_number(safe_get(info, "volume")),
            "Avg Volume": format_large_number(safe_get(info, "averageVolume")),
        }
        df_price = pd.DataFrame(price_info.items(), columns=["Field", "Value"])

        valuation = {
            "Market Cap": format_large_number(safe_get(info, "marketCap")),
            "PE Ratio": format_number(safe_get(info, "trailingPE")),
            "EPS": format_number(safe_get(info, "trailingEps")),
            "PB Ratio": format_number(safe_get(info, "priceToBook")),
            "Dividend Yield": format_number(safe_get(info, "dividendYield")),
            "ROE": format_number(safe_get(info, "returnOnEquity")),
            "ROA": format_number(safe_get(info, "returnOnAssets")),
        }
        df_val = pd.DataFrame(valuation.items(), columns=["Field", "Value"])

        extra = {
            "Beta": format_number(safe_get(info, "beta")),
            "Revenue": format_large_number(safe_get(info, "totalRevenue")),
            "Gross Margins": format_number(safe_get(info, "grossMargins")),
            "Operating Margins": format_number(safe_get(info, "operatingMargins")),
            "Profit Margins": format_number(safe_get(info, "profitMargins")),
            "Book Value": format_number(safe_get(info, "bookValue")),
        }
        df_extra = pd.DataFrame(extra.items(), columns=["Field", "Value"])

        final_html = (
            html_card("Basic Information", make_table(df_basic))
            + html_card("Price Details", make_table(df_price))
            + html_card("Valuation Metrics", make_table(df_val))
            + html_card("Additional Company Data", make_table(df_extra))
        )
        return final_html

    except Exception as e:
        return html_error(f"INFO ERROR: {e}<br><pre>{traceback.format_exc()}</pre>")


# -------------------------- INTRADAY ------------------------------

def fetch_intraday(symbol, indicators=None):
    try:
        df = intraday(symbol)
        if df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        chart_html = build_chart(df, indicators=indicators, volume=True)
        table_html = make_table(df.tail(50))

        return wrap_html(f"{chart_html}<h2>Last 50 Rows</h2>{table_html}",
                         title=f"{symbol} Intraday")

    except Exception as e:
        return wrap_html(f"<h1>Error:{e}</h1>")


# -------------------------- DAILY ------------------------------

def fetch_daily(symbol, source="yfinance", max_rows=200):
    try:
        df = daily(symbol)
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
