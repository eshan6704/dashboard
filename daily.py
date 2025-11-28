import yfinance as yf
import pandas as pd
import io
import requests

from datetime import datetime, timedelta
from ta_indi_pat import talib_df  # use the combined talib_df function
from common import html_card, wrap_html
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
