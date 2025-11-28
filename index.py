import io
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from common import html_card, wrap_html
from ta_indi_pat import talib_df
import datetime
import nse


def fetch_index(max_rows=200):
    """
    Fetch NIFTY 50 (^NSEI) 1-year OHLCV data from Yahoo Finance,
    add TA-Lib indicators + candlestick patterns,
    return HTML table inside a scrollable container.
    """

    try:
        # ----------------------------------
        # Fetch NIFTY 50 data
        # ----------------------------------
        df = nse_index_df(index_name="NIFTY 50"):
        

        if df.empty:
            return html_card("Error", "No data found for NIFTY 50 (^NSEI).")

        # Standardize column names
        df.columns = ["Close", "High", "Low", "Open", "Volume"]
        df.reset_index(inplace=True)  # make Date a column

        # Limit display rows
        df_display = df



        # ----------------------------------
        # Convert to HTML
        # ----------------------------------
        table_html = df_display.to_html(
            classes="table table-striped table-bordered",
            index=False
        )

        scrollable_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:650px; border:1px solid #ccc; padding:8px;">
            {table_html}
        </div>
        """

        content = f"""
        <h2>NIFTY 50 </h2>
        {html_card("Technical Analysis Table", scrollable_html)}
        """

        return wrap_html(content, title="NIFTY 50 Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
