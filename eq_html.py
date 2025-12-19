from nsepython import *
import os
import pickle
import pandas as pd
from datetime import datetime

# =====================================================
# CACHE CONFIG (DAILY VALIDITY)
# =====================================================
CACHE_DIR = "./cache/eq"
os.makedirs(CACHE_DIR, exist_ok=True)


def _today_key():
    return datetime.now().strftime("%Y%m%d")


def _path(name):
    return os.path.join(CACHE_DIR, name)


def cache_load(name):
    try:
        with open(_path(name), "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def cache_save(name, obj):
    with open(_path(name), "wb") as f:
        pickle.dump(obj, f)


# =====================================================
# MAIN FUNCTION (DO NOT RENAME)
# =====================================================
def build_eq_html(symbol):
    """
    Build full HTML page for eq(symbol)
    Cache rules:
    - HTML cached per (symbol + day)
    - EQ raw output cached per (symbol + day)
    """

    day = _today_key()
    symbol = symbol.upper()

    html_key = f"eq_html_{symbol}_{day}.pkl"
    raw_key = f"eq_raw_{symbol}_{day}.pkl"

    # --------------------------------------------------
    # 1️⃣ HTML CACHE FIRST
    # --------------------------------------------------
    html = cache_load(html_key)
    if html:
        return html

    # --------------------------------------------------
    # 2️⃣ RAW EQ CACHE
    # --------------------------------------------------
    out = cache_load(raw_key)
    if not out:
        out = eq(symbol)   # 🔥 existing nsepython function
        if not isinstance(out, dict):
            return "<h3>Error: EQ data not available</h3>"
        cache_save(raw_key, out)

    # --------------------------------------------------
    # 3️⃣ DF → HTML TABLE
    # --------------------------------------------------
    def df_to_table(df):
        if df is None or df.empty:
            return '<div class="empty">No data</div>'
        return df.to_html(
            index=False,
            escape=False,
            border=0,
            classes="tbl"
        )

    # --------------------------------------------------
    # 4️⃣ SECTION ORDER (METADATA FIRST)
    # --------------------------------------------------
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

    # --------------------------------------------------
    # 5️⃣ BUILD SECTION HTML
    # --------------------------------------------------
    section_html = ""
    for sec in section_order:
        section_html += f"""
        <div class="section">
            <div class="section-header">
                <div class="section-title">{sec}</div>
                <button class="toggle-btn" onclick="toggleSection('{sec}')">
                    View / Hide
                </button>
            </div>
            <div id="{sec}" class="section-body">
                {df_to_table(normalized[sec])}
            </div>
        </div>
        """

    # --------------------------------------------------
    # 6️⃣ FINAL HTML
    # --------------------------------------------------
    html = f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #fafafa;
            margin: 0;
            padding: 12px;
        }}
        h2 {{
            color: #0366d6;
            margin-bottom: 10px;
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
            font-size: 15px;
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
            const e = document.getElementById(id);
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

    # --------------------------------------------------
    # 7️⃣ SAVE HTML CACHE
    # --------------------------------------------------
    cache_save(html_key, html)

    return html
