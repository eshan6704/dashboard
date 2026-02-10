from app.nse import nsepythonmodified as ns
import pandas as pd
from datetime import datetime


def build_eq_html(symbol):
    """
    Build full HTML page for eq(symbol) output
    Returns: HTML string
    """

    # -------------------------------------------------------
    # CALL eq() function
    # -------------------------------------------------------
    try:
        out = ns.eq(symbol)
        print(f"DEBUG - API Response for {symbol}:", out)
    except Exception as e:
        print(f"DEBUG - Error calling ns.eq({symbol}):", str(e))
        return f"<h3>Error: Failed to fetch data for {symbol}</h3>"

    if not isinstance(out, dict):
        print(f"DEBUG - Invalid response type:", type(out))
        return "<h3>Error: EQ data not available</h3>"

    # -------------------------------------------------------
    # Helper: DataFrame → HTML table
    # -------------------------------------------------------
    def df_to_table(df):
        if df is None or df.empty:
            return '<div class="empty">No data</div>'
        return df.to_html(index=False, escape=False, border=0, classes="tbl")

    # -------------------------------------------------------
    # ORDER
    # -------------------------------------------------------
    section_order = [
        "metadata",
        "securityInfo",
        "priceInfo",
        "industryInfo",
        "pdSectorIndAll",
        "info",
        "preOpen",
        "preOpenMarket"
    ]

    # Normalize to DataFrames
    normalized = {}
    for sec in section_order:
        val = out.get(sec)
        if isinstance(val, pd.DataFrame):
            normalized[sec] = val
        elif isinstance(val, list):
            normalized[sec] = pd.DataFrame(val)
        elif isinstance(val, dict):
            normalized[sec] = pd.DataFrame([val])
        else:
            normalized[sec] = pd.DataFrame()

    # -------------------------------------------------------
    # Sections HTML
    # -------------------------------------------------------
    section_html = ""
    for sec in section_order:
        section_html += f"""
        <div class="section">
            <div class="section-header">
                <div class="section-title">{sec}</div>
                <button class="toggle-btn" onclick="toggleSection('{sec}')">View / Hide</button>
            </div>
            <div id="{sec}" class="section-body">
                {df_to_table(normalized[sec])}
            </div>
        </div>
        """

    # -------------------------------------------------------
    # FINAL HTML
    # -------------------------------------------------------
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Equity Report - {symbol}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #fafafa;
    margin: 0;
    padding: 12px;
}}
h2 {{
    color: #0366d6;
}}
.section {{
    background: #fff;
    border: 1px solid #ddd;
    margin-bottom: 14px;
    padding: 12px;
    border-radius: 6px;
}}
.section-header {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}}
.section-title {{
    font-weight: bold;
    color: #0b69a3;
}}
.toggle-btn {{
    background: #0b69a3;
    color: #fff;
    border: none;
    padding: 6px 10px;
    font-size: 12px;
    border-radius: 5px;
    cursor: pointer;
}}
.tbl {{
    border-collapse: collapse;
    width: 100%;
    font-size: 13px;
}}
.tbl th {{
    background: #0b69a3;
    color: #fff;
    padding: 6px;
    border: 1px solid #ccc;
}}
.tbl td {{
    padding: 6px;
    border: 1px solid #ccc;
}}
.empty {{
    padding: 10px;
    color: #777;
}}
</style>

<script>
function toggleSection(id) {{
    let e = document.getElementById(id);
    e.style.display = (e.style.display === "none") ? "block" : "none";
}}
</script>
</head>

<body>
<h2>Equity Report — {symbol}</h2>
{section_html}
</body>
</html>
"""

    return html
