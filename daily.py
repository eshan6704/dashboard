'''import yfinance as yf
import pandas as pd
import io
import requests
from  nse import daily
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
'''
import io
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from common import html_card, wrap_html
from ta_indi_pat import talib_df
import datetime
from nse import nse_index_df


def fetch_index(max_rows=200):
    """
    Fetch NIFTY 50 data using nse_index_df(),
    format each returned DataFrame into its own HTML table.
    """

    try:
        # ------------------------------------------------
        # Fetch NIFTY 50 → 4 dataframes
        # ------------------------------------------------
        df_market, df_adv, df_meta, df_data = nse_index_df(index_name="NIFTY 50")

        # Debug print
        print("MARKET DF:", df_market.shape)
        print("ADVANCE DECLINE DF:", df_adv.shape)
        print("META DF:", df_meta.shape)
        print("DATA DF:", df_data.shape)

        # ------------------------------------------------
        # Helper for HTML conversion
        # ------------------------------------------------
        def make_table(df):
            return f"""
            <div style="overflow-x:auto; overflow-y:auto; max-height:450px; border:1px solid #ccc; padding:8px; margin-bottom:18px;">
                {df.to_html(classes='table table-striped table-bordered', index=False)}
            </div>
            """

        # Convert all tables
        html_market = make_table(df_market)
        html_adv    = make_table(df_adv)
        html_meta   = make_table(df_meta)
        html_data   = make_table(df_data)

        # ------------------------------------------------
        # Final HTML layout
        # ------------------------------------------------
        content = f"""
        <h2>NIFTY 50 - Index Report</h2>

        {html_card("Market Overview", html_market)}
        {html_card("Advance / Decline", html_adv)}
        {html_card("Index Meta Information", html_meta)}
        {html_card("Daily OHLCV + Calculated Indicators", html_data)}
        """

        return wrap_html(content, title="NIFTY 50 Index Data")

    except Exception as e:
        return html_card("Error", str(e))
