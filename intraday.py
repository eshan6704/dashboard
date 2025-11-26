# intraday.py

import yfinance as yf
import pandas as pd
from chart_builder import build_chart


# -------------------------------
# Fetch + Clean intraday dataset
# -------------------------------
def _fetch_intraday(symbol, interval="5m", period="1d"):
    yfs = f"{symbol}.NS"

    try:
        df = yf.download(
            yfs,
            interval=interval,
            period=period,
            progress=False
        )
    except Exception as e:
        return None, str(e)

    if df is None or df.empty:
        return None, "No intraday data returned"

    # Clean index timestamps
    df.index = pd.to_datetime(df.index)

    # Remove timezone if present
    try:
        df.index = df.index.tz_localize(None)
    except:
        pass

    # Round values
    df = df.round(2)

    return df, None


# -------------------------------
# Main intraday function (UI return)
# -------------------------------
def fetch_intraday(symbol, interval="5m", period="1d"):
    """
    Supported:
        interval = 1m,2m,5m,15m,30m,60m
        period   = 1d,5d,1mo
    """

    df, err = _fetch_intraday(symbol, interval, period)

    if err:
        return {
            "html": f"<div class='group'><h2>Intraday Error</h2><p>{err}</p></div>",
            "data": {}
        }

    if df is None or df.empty:
        return {
            "html": f"<div class='group'><h2>No Intraday Data for {symbol}</h2></div>",
            "data": {}
        }

    # Build chart using indicator engine
    chart_html = build_chart(df)

    # Convert last rows to table
    table_html = df.tail(200).to_html(
        classes="styled-table",
        border=0
    )

    final = f"""
    <div class="group">
        <h2>Intraday Chart — {symbol} ({interval}, {period})</h2>
        {chart_html}

        <h3>Last 200 Rows</h3>
        {table_html}

        <style>
            .styled-table {{
                border-collapse: collapse;
                width: 100%;
                font-size: 13px;
            }}
            .styled-table td, .styled-table th {{
                border: 1px solid #ddd;
                padding: 6px;
                text-align: right;
            }}
            .styled-table tr:nth-child(even) {{background: #f9f9f9;}}
        </style>
    </div>
    """

    return {
        "html": final,
        "data": df.tail(200).to_dict()
    }
