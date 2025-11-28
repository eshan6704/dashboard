# ============================
# info.py — Company Info Page
# EXACT SAME LOOK AS BEFORE
# ============================

import yfinance as yf
import pandas as pd
import traceback

from yf import yfinfo

from common import (format_number,format_large_number,make_table,html_card,html_section,html_error,clean_df,safe_get)


def fetch_info(symbol: str):
    """
    Fetch full company info and return the SAME layout you used earlier.
    Only internal code updated to use common.py helpers.
    """
    try:
        tk=info(symbol)
        info = tk.info

        if not info:
            return html_error(f"No information found for {symbol}")

        # ===== BASIC DETAILS =====
        basic = {
            "Symbol": symbol,
            "Name": safe_get(info, "longName"),
            "Sector": safe_get(info, "sector"),
            "Industry": safe_get(info, "industry"),
            "Website": safe_get(info, "website"),
            "Employee Count": format_large_number(safe_get(info, "fullTimeEmployees")),
        }
        df_basic = pd.DataFrame(basic.items(), columns=["Field", "Value"])
        basic_html = make_table(df_basic)

        # ===== PRICE DETAILS =====
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
        price_html = make_table(df_price)

        # ===== VALUATION METRICS =====
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
        val_html = make_table(df_val)

        # ===== COMPANY EXTRA DETAILS =====
        extra = {
            "Beta": format_number(safe_get(info, "beta")),
            "Revenue": format_large_number(safe_get(info, "totalRevenue")),
            "Gross Margins": format_number(safe_get(info, "grossMargins")),
            "Operating Margins": format_number(safe_get(info, "operatingMargins")),
            "Profit Margins": format_number(safe_get(info, "profitMargins")),
            "Book Value": format_number(safe_get(info, "bookValue")),
        }
        df_extra = pd.DataFrame(extra.items(), columns=["Field", "Value"])
        extra_html = make_table(df_extra)

        # ========================
        # Final HTML (Same Layout)
        # ========================
        final_html = (
            html_card("Basic Information", basic_html)
            + html_card("Price Details", price_html)
            + html_card("Valuation Metrics", val_html)
            + html_card("Additional Company Data", extra_html)
        )

        return final_html

    except Exception as e:
        return html_error(f"INFO MODULE ERROR: {e}<br><pre>{traceback.format_exc()}</pre>")
