# qresult.py
import yfinance as yf
import pandas as pd
from common import make_table, wrap_html, format_large_number, html_error

def fetch_qresult(symbol):
    """
    Fetch quarterly financials for a stock symbol and return HTML
    """
    yfsymbol = symbol + ".NS"
    try:
        ticker = yf.Ticker(yfsymbol)
        df = ticker.quarterly_financials

        if df.empty:
            return wrap_html(f"<h1>No quarterly results available for {symbol}</h1>")

        # Format numeric columns
        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        # Format index (dates)
        df_formatted.index = [str(i.date()) if hasattr(i, "date") else str(i) for i in df_formatted.index]

        # Convert to pretty HTML table
        table_html = make_table(df_formatted)

        # Wrap into full HTML page
        return wrap_html(table_html, title=f"{symbol} - Quarterly Results")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch quarterly results: {e}"))
