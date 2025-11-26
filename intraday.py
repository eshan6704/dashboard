# intraday.py
import yfinance as yf
import pandas as pd
from common import format_large_number, wrap_html, make_table
from chart_builder import build_chart

# ============================================================
#               INTRADAY DATA PROCESSING
# ============================================================

def fetch_intraday(symbol, indicators=None):
    """
    Fetch intraday (5-min) data for a symbol from Yahoo Finance,
    format it, apply indicators, and return full HTML.
    """
    yfsymbol = f"{symbol}.NS"
    try:
        # Fetch 1-day intraday 5-min interval
        df = yf.download(yfsymbol, period="1d", interval="5m").round(2)
        if df.empty:
            return wrap_html(f"<h1>No intraday data available for {symbol}</h1>")

        # Reset MultiIndex if exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Build chart with indicators
        chart_html = build_chart(df, indicators=indicators, volume=True)

        # Format last 50 rows for table
        table_html = make_table(df.tail(50))

        # Wrap in full HTML
        full_html = wrap_html(f"{chart_html}<h2>Recent Intraday Data (last 50 rows)</h2>{table_html}",
                              title=f"Intraday Data for {symbol}")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetching intraday data for {symbol}</h1><p>{str(e)}</p>")
