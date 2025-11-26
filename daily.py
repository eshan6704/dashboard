# daily.py
import yfinance as yf
import pandas as pd
from ta_indi_pat import patterns, indicators
from common import html_card, wrap_html

def fetch_daily(symbol, max_rows=200):
    """
    Fetch daily OHLCV data, calculate indicators + patterns, handle multilevel headers,
    and return a scrollable HTML table (x and y).
    """
    try:
        # --- Fetch historical data ---
        df = yf.download(symbol + ".NS", period="1y", interval="1d").round(2)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return html_card("Error", f"No daily data found for {symbol}")
        df.reset_index(inplace=True)

        # --- Calculate indicators and patterns ---
        indicator_df = indicators(df)
        pattern_df = patterns(df)

        # --- Combine OHLCV + indicators + patterns ---
        combined_df = pd.concat([df, indicator_df, pattern_df], axis=1)

        # --- Handle MultiIndex columns: take only 0th level ---
        if isinstance(combined_df.columns, pd.MultiIndex):
            combined_df.columns = combined_df.columns.get_level_values(0)

        # --- Limit rows for display ---
        combined_df = combined_df.head(max_rows)

        # --- Convert to HTML table ---
        table_html = combined_df.to_html(classes="table table-striped table-bordered", border=0, index=False)

        # --- Wrap table in scrollable div ---
        scrollable_table_html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:600px; border:1px solid #ccc; padding:5px;">
            {table_html}
        </div>
        """

        # --- Wrap in card and full HTML ---
        content = f"""
        <h2>{symbol} - Daily Data</h2>
        {html_card("Data Table", scrollable_table_html)}
        """

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return html_card("Error", str(e))
