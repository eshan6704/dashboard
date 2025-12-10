from nsepython import *
import pandas as pd
import json

def df_to_html(df):
    """Convert DataFrame to HTML table (static, no JS)."""
    if df.empty:
        return "<p>No data available.</p>"

    # Start table
    html = "<table><thead><tr>"

    # Headers
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    # Rows
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            html += f"<td>{row[col]}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html


def build_index_live_html(name=""):
    # Fetch data (default index)
    p = nse_index_live()

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    # Convert to static HTML tables
    rem_html = df_to_html(rem_df)
    full_html = df_to_html(full_df)

    # ---- Final static HTML (no <script>) ----
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: Arial;
    margin: 15px;
    background: #f5f5f5;
}}
h2, h3 {{
    margin-bottom: 10px;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
    background: white;
}}
th, td {{
    border: 1px solid #ccc;
    padding: 6px 8px;
    text-align: left;
}}
th {{
    background: #333;
    color: white;
}}
</style>
</head>
<body>

<h2>Live Index Data — {name or "Default Index"}</h2>

<h3>Index Info (rem)</h3>
{rem_html}

<h3>Full Index Data</h3>
{full_html}

</body>
</html>
"""
    return html
