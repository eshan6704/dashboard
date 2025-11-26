import pandas as pd
import numpy as np
import traceback

# ============================================================
#                   NUMBER FORMATTING HELPERS
# ============================================================

def format_number(num):
    """Format numbers with commas, handle None, remove trailing zeros."""
    if num is None:
        return "-"
    try:
        return f"{float(num):,.2f}".rstrip("0").rstrip(".")
    except:
        return str(num)


def format_large_number(num):
    """Format large numbers into K, Lakh, Crore."""
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
    """Beautiful card-style container."""
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
    """Simple titled section."""
    return f"""
    <div style="margin:20px 0;">
        <h3 style="color:#444;margin-bottom:8px;">{title}</h3>
        {content}
    </div>
    """


def html_error(msg):
    """Red error block with message."""
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
    """Standard cleanup for all results."""
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime("%Y-%m-%d")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("-", inplace=True)
    return df

# ============================================================
#                   TABLE STYLING
# ============================================================

def make_table(df):
    """Convert DataFrame to pretty HTML table."""
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
    """Wrap chart + optional table into same styled page."""
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
    """Sometimes JSON keys are missing; avoid crash."""
    try:
        return df.get(key, default_val)
    except:
        return default_val
def format_timestamp_to_date(timestamp):
    if not isinstance(timestamp, (int, float)) or timestamp <= 0:
        return "N/A"
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception:
        return "Invalid Date"

