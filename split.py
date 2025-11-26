# split.py
import yfinance as yf
import pandas as pd
import pandas.api.types as ptypes
import datetime

# --- CSS for this module ---
STYLE_BLOCK = """
<style>
.styled-table {
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 0.9em;
  font-family: sans-serif;
  width: 100%;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.styled-table th, .styled-table td {
  padding: 8px 10px;
  border: 1px solid #ddd;
}
.styled-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}
.card {
  width: 95%;
  margin: 10px auto;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.card h2 {
  margin-top:0;
}
</style>
"""

def format_large_number(num):
    if not isinstance(num, (int, float)):
        return num
    sign = '-' if num < 0 else ''
    num = abs(float(num))
    if num >= 1_000_000_000_000:
        return f"{sign}{num / 1_000_000_000_000:.2f} LCr"
    elif num >= 10_000_000:
        return f"{sign}{num / 10_000_000:.2f} Cr"
    elif num >= 100_000:
        return f"{sign}{num / 100_000:.2f} Lac"
    else:
        return f"{sign}{num:,.0f}"

def fetch_split(symbol):
    yfsymbol = f"{symbol}.NS"
    try:
        ticker = yf.Ticker(yfsymbol)
        df = ticker.splits.to_frame('Split')
        if df.empty:
            content_html = f"<h1>No split history available for {symbol}</h1>"
        else:
            # Format numeric columns
            for col in df.columns:
                if ptypes.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(format_large_number)
            content_html = f"<div class='card'><h2>Stock Split History</h2>{df.to_html(classes='styled-table', border=0)}</div>"
    except Exception as e:
        content_html = f"<h1>Error</h1><p>{str(e)}</p>"

    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stock Split History for {symbol}</title>
    {STYLE_BLOCK}
</head>
<body>
    {content_html}
</body>
</html>
"""
    return full_html
