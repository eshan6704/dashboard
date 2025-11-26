# daily.py
import yfinance as yf
import pandas as pd
from ta_indi_pat import patterns, indicators
from common import html_card, wrap_html

def fetch_daily(symbol, max_rows=200):
    """
    Fetch daily OHLCV data, calculate indicators + patterns,
    and return 3 separate scrollable HTML tables: OHLCV, indicators, patterns.
    """
    try:
        # --- Fetch historical data ---
        df = yf.download(symbol + ".NS", period="1y", interval="1d").round(2)
 
        #if isinstance(df.columns, pd.MultiIndex):
                #df.columns = df.columns.get_level_values(0)
        df.columns=["Close",	"High",	"Low",	"Open",	"Volume"]
        if df.empty:
            return html_card("Error", f"No daily data found for {symbol}")
        df.reset_index(inplace=True)
        df = df.head(max_rows)

        # --- Calculate indicators and patterns ---
        indicator_df = indicators(df).head(max_rows)
        pattern_df = patterns(df).head(max_rows)

        # --- Handle MultiIndex columns: take only 0th level ---


        # --- Convert each DataFrame to HTML table ---
        daily_table_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:400px; border:1px solid #ccc; padding:5px;">
            {df.to_html(classes="table table-striped table-bordered", index=False)}
        </div>
        """
        indicator_table_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:400px; border:1px solid #ccc; padding:5px;">
            {indicator_df.to_html(classes="table table-striped table-bordered", index=False)}
        </div>
        """
        pattern_table_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:400px; border:1px solid #ccc; padding:5px;">
            {pattern_df.to_html(classes="table table-striped table-bordered", index=False)}
        </div>
        """

        # --- Wrap each in card ---
        content = f"""
        <h2>{symbol} - Daily Data</h2>
        {html_card("Daily OHLCV Data", daily_table_html)}
        {html_card("Indicator Data", indicator_table_html)}
        {html_card("Pattern Data", pattern_table_html)}
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
