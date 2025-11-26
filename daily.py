# daily.py
import yfinance as yf
import pandas as pd
from indicater import calculate_indicators
from chart_builder import build_chart
from common import html_card, html_section, wrap_html, clean_df, make_table

def fetch_daily(symbol):
    try:
        # --- Fetch data from Yahoo Finance ---
        data = yf.download(symbol + ".NS", period="6mo", interval="1d", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)  # flatten multi-level header

        # Ensure OHLCV columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col not in data.columns:
                data[col] = 0

        data = clean_df(data)

        # --- Calculate all indicators ---
        indicators = calculate_indicators(data)

        # --- Build Plotly chart ---
        chart_html = build_chart(data, indicators)

        # --- Build data table for the same DataFrame + indicators ---
        df_table = data.copy()
        for ind_name, ind_series in indicators.items():
            df_table[ind_name] = ind_series

        table_html = make_table(df_table)

        # --- Wrap chart + table in card ---
        content = html_card(f"{symbol} Daily Chart", chart_html + table_html)

        return wrap_html(content, title=f"{symbol} Daily Data")

    except Exception as e:
        return wrap_html(html_section("Error", str(e)), title="Error")
