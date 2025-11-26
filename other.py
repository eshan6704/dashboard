# other.py
import yfinance as yf
from common import make_table, wrap_html, format_large_number, html_error

def fetch_other(symbol):
    yfsymbol = symbol + ".NS"
    try:
        ticker = yf.Ticker(yfsymbol)
        df = ticker.earnings

        if df.empty:
            return wrap_html(f"<h1>No earnings data available for {symbol}</h1>")

        df_formatted = df.copy()
        for col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_formatted.index = [str(i) for i in df_formatted.index]
        table_html = make_table(df_formatted)

        return wrap_html(table_html, title=f"{symbol} - Earnings")

    except Exception as e:
        return wrap_html(html_error(f"Failed to fetch earnings data: {e}"))
