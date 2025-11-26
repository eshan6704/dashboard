# qresult.py
import yfinance as yf
import pandas as pd
from common import (
    format_large_number,
    format_timestamp_to_date,
    format_number,
    wrap_html,
    STYLE_BLOCK
)

def fetch_qresult(symbol):
    yfsymbol = f"{symbol}.NS"

    try:
        ticker = yf.Ticker(yfsymbol)

        # Fetch data
        q = ticker.quarterly_financials
        y = ticker.financials
        bs = ticker.balance_sheet
        cf = ticker.cashflow

        if q is None or q.empty:
            return wrap_html(
                f"Quarterly Results: {symbol}",
                "<h2>No quarterly data available</h2>"
            )

        # Transpose for nicer table format
        q_t = q.T
        y_t = y.T if y is not None else None
        bs_t = bs.T if bs is not None else None
        cf_t = cf.T if cf is not None else None

        # ------------------------
        def format_df(df):
            df_formatted = df.copy()
    
            # Format numeric columns
            for col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: format_number(x) if isinstance(x, (int, float)) else x
                )

            # Fix index (assume index is datetime-like)
            df_formatted.index = [
                format_timestamp_to_date(i.timestamp()) if hasattr(i, "timestamp") else str(i)
                for i in df_formatted.index
            ]

            return df_formatted


        q_html = format_df(q_t).to_html(classes="styled-table", border=0)

        y_html = ""
        if y_t is not None:
            y_html = format_df(y_t).to_html(classes="styled-table", border=0)

        bs_html = ""
        if bs_t is not None:
            bs_html = format_df(bs_t).to_html(classes="styled-table", border=0)

        cf_html = ""
        if cf_t is not None:
            cf_html = format_df(cf_t).to_html(classes="styled-table", border=0)

        # Build sections
        content = f"""
        <div class='big-box'>
            <h2>Quarterly Results</h2>
            {q_html}
        </div>
        """

        if y_html:
            content += f"""
            <div class='big-box'>
                <h2>Annual Results</h2>
                {y_html}
            </div>
            """

        if bs_html:
            content += f"""
            <div class='big-box'>
                <h2>Balance Sheet</h2>
                {bs_html}
            </div>
            """

        if cf_html:
            content += f"""
            <div class='big-box'>
                <h2>Cash Flow</h2>
                {cf_html}
            </div>
            """

        return wrap_html(f"Quarterly Results — {symbol}", content)

    except Exception as e:
        return wrap_html("Error", f"<h3>Error fetching results</h3><p>{str(e)}</p>")
