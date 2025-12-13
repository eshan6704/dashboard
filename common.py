import pandas as pd
import numpy as np
import datetime
import traceback
from backblaze import *

# ============================================================
#                   NUMBER FORMATTING HELPERS
# ============================================================

def format_number(num):
    if num is None:
        return "-"
    try:
        return f"{float(num):,.2f}".rstrip("0").rstrip(".")
    except:
        return str(num)

def format_large_number(num):
    if num is None:
        return "-"
    try:
        n = float(num)
        if abs(n) >= 1_00_00_000:     # Crore
            return f"{n/1_00_00_000:.2f} Cr"
        elif abs(n) >= 1_00_000:      # Lakh
            return f"{n/1_00_000:.2f} L"
        elif abs(n) >= 1_000:         # Thousand
            return f"{n/1_000:.2f} K"
        else:
            return format_number(n)
    except:
        return str(num)

# ============================================================
#                   HTML UI HELPERS
# ============================================================

def html_card(title, content):
    return f"""
    <div style="
        background:#fff;
        border-radius:12px;
        padding:18px;
        margin:15px 0;
        box-shadow:0 2px 8px rgba(0,0,0,0.1);
        border-left:6px solid #0077cc;
    ">
        <h2 style="margin-top:0;color:#0077cc;">{title}</h2>
        <div>{content}</div>
    </div>
    """

def html_section(title, content):
    return f"""
    <div style="margin:20px 0;">
        <h3 style="color:#444;margin-bottom:8px;">{title}</h3>
        {content}
    </div>
    """

def html_error(msg):
    return f"""
    <div style="
        padding:15px;
        margin:15px 0;
        background:#ffe6e6;
        border-left:6px solid #d9534f;
        border-radius:8px;
        color:#b30000;
    ">
        <b>Error:</b> {msg}
    </div>
    """

# ============================================================
#                   DATAFRAME CLEANING
# ============================================================

def clean_df(df):
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime("%Y-%m-%d")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("-", inplace=True)
    return df

# ============================================================
#                   TABLE STYLING
# ============================================================

def make_table(df):
    try:
        df = df.copy()
        df = clean_df(df)
        html = df.to_html(classes="styled-table", escape=False, border=0)
        return f"""
        <style>
        .styled-table {{
            width:100%;
            border-collapse:collapse;
            font-size:14px;
        }}
        .styled-table th {{
            background:#0077cc;
            color:white;
            padding:8px;
            text-align:left;
        }}
        .styled-table td {{
            padding:8px;
            border-bottom:1px solid #ddd;
        }}
        .styled-table tr:nth-child(even) {{
            background:#f3f7ff;
        }}
        .styled-table tr:hover {{
            background:#e7f1ff;
        }}
        </style>
        {html}
        """
    except Exception as e:
        return html_error(f"Table render failed: {e}<br><pre>{traceback.format_exc()}</pre>")

# ============================================================
#                   UNIVERSAL PLOT WRAPPER
# ============================================================

def wrap_plotly_html(html_chart, table_html=None):
    extra = f"<div style='margin-top:20px'>{table_html}</div>" if table_html else ""
    return f"""
    <div style="width:98%;margin:auto;">
        {html_card("Chart", html_chart)}
        {extra}
    </div>
    """

# ============================================================
#               INDICATOR SAFE EXTRACTION HELPER
# ============================================================

def safe_get(df, key, default_val="-"):
    try:
        return df.get(key, default_val)
    except:
        return default_val

def format_timestamp_to_date(timestamp):
    if not isinstance(timestamp, (int, float)) or timestamp <= 0:
        return "N/A"
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return "Invalid Date"

# ============================================================
#                   HTML WRAPPER
# ============================================================

STYLE_BLOCK = """
<style>
.styled-table {border-collapse: collapse; margin: 10px 0; font-size: 0.9em; font-family: sans-serif; width: 100%; box-shadow: 0 0 10px rgba(0,0,0,0.1);}
.styled-table th, .styled-table td {padding: 8px 10px; border: 1px solid #ddd;}
.styled-table tbody tr:nth-child(even) {background-color: #f9f9f9;}
.card {display: block; width: 95%; margin: 10px auto; padding: 15px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); background: #fafafa;}
.card-category-title {font-size: 1.1em; color: #222; margin: 0 0 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;}
.card-content-grid {display: flex; flex-wrap: wrap; gap: 15px;}
.key-value-pair {flex: 1 1 calc(20% - 15px); box-sizing: border-box; min-width: 150px; background: #fff; padding: 10px; border: 1px solid #e0e0e0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
.key-value-pair h3 {font-size: 0.95em; color: #444; margin: 0 0 5px 0;}
.key-value-pair p {font-size: 0.9em; color: #555; margin: 0; font-weight: bold;}
.big-box {width:95%; margin:20px auto; padding:20px; border:1px solid #ccc; border-radius:8px; background:#fff; box-shadow:0 2px 8px rgba(0,0,0,0.1); font-size:0.95em; line-height:1.4em; max-height:400px; overflow-y:auto;}
</style>
"""

def wrap_html(content, title="Stock Data"):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    {STYLE_BLOCK}
</head>
<body>
    {content}
</body>
</html>
"""
# ======================================================
# Scrollable HTML wrapper
# ======================================================
SCROLL_WRAP = """
<div style="
    max-height: 80vh;
    overflow-y: auto;
    overflow-x: auto;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
">
{{HTML}}
</div>
"""

# ======================================================
# Date helpers
# ======================================================
def today_str():
    return datetime.date.today().strftime("%d-%m-%Y")

def yesterday_str():
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")

def last_year_date(d):
    dt = datetime.datetime.strptime(d, "%d-%m-%Y")
    new_dt = dt.replace(year=dt.year - 1)
    return new_dt.strftime("%d-%m-%Y")

# ======================================================
# HTML wrapper
# ======================================================
def wrap(html):
    if html is None:
        return "<h3>No Data</h3>"
    return SCROLL_WRAP.replace("{{HTML}}", html)