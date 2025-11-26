# daily.py
import pandas as pd
import yfinance as yf
from common import wrap_html, html_error, clean_df, make_table
from indicater import calculate_indicators
from chart_builder import build_chart

def fetch_daily(symbol):
    """
    Fetches daily OHLCV data, calculates indicators, builds chart, 
    and returns the complete HTML for Gradio UI.
    """
    try:
        yfsymbol = symbol + ".NS"

        # ---------------- Fetch daily data ----------------
        df = yf.download(yfsymbol, period="6mo", interval="1d")
        if df.empty:
            return html_error(f"No daily data found for {symbol}")

        df = clean_df(df)

        # ---------------- Calculate indicators ----------------
        indicators = calculate_indicators(df)

        # ---------------- Build chart ----------------
        html_chart = build_chart(df, indicators)

        # ---------------- Build table ----------------
        table_html = make_table(df)

        # ---------------- Wrap into full HTML ----------------
        html = wrap_html(f"{html_chart}<br>{table_html}", title=f"{symbol} Daily Chart")
        return html

    except Exception as e:
        return html_error(f"Error generating daily chart for {symbol}: {e}")
