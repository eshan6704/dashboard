
from app.nse import nsepythonmodified as ns

import pandas as pd
from datetime import datetime
import os

# ==============================
# Simple daily cache helpers
# ==============================
CACHE_DIR = "./cache_eq"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.html")

def _is_today(path):
    if not os.path.exists(path):
        return False
    mtime = datetime.fromtimestamp(os.path.getmtime(path)).date()
    return mtime == datetime.now().date()

def cache_load(key):
    path = _cache_path(key)
    if _is_today(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return False
    return False

def cache_save(key, html):
    with open(_cache_path(key), "w", encoding="utf-8") as f:
        f.write(html)

# ==============================
# MAIN FUNCTION (CACHED)
# ==============================
def build_eq_html(symbol):
    """
    Build full HTML page for eq(symbol) output
    DAILY CACHED
    """

    cache_key = f"eq_{symbol.upper()}"

    # ---------- CACHE HIT ----------
    cached = cache_load(cache_key)

    # -------------------------------------------------------
    # CALL eq() function
    # -------------------------------------------------------
    out = ns.eq(symbol)

    if not isinstance(out, dict):
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

    # ---------- SAVE CACHE ----------
 
    return html