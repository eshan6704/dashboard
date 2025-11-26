# daily.py
import yfinance as yf
import pandas as pd
from common import wrap_html, make_table
from chart_builder import build_chart

# ============================================================
#                  DAILY DATA PROCESSING
# ============================================================

def fetch_daily(symbol, indicators=None):
    """
    Fetch daily data for 1 year, apply indicators, and return full HTML.
    """
    yfsymbol = f"{symbol}.NS"
    try:
        # Fetch 1-year daily data
        df = yf.download(yfsymbol, period="1y", interval="1d").round(2)
        if df.empty:
            return wrap_html(f"<h1>No daily data available for {symbol}</h1>")

        # Reset MultiIndex if exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Build chart with optional indicators
        chart_html = build_chart(df, indicators=['macd','supertrend','keltner','zigzag','swing','stockstick'])

        #chart_html = build_chart(df, indicators=indicators, volume=True)

        # Format last 30 rows for table
        table_html = make_table(df.tail(30))

        # Wrap in full HTML
        full_html = wrap_html(f"{chart_html}<h2>Recent Daily Data (last 30 rows)</h2>{table_html}",
                              title=f"Daily Data for {symbol}")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetching daily data for {symbol}</h1><p>{str(e)}</p>")
