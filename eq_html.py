from nsepython import *
def build_eq_html(symbol):
    """Build full HTML page for eq(symbol) output, similar to build_indices_html."""

    import json
    import pandas as pd

    # -------------------------------------------------------
    # CALL eq() function internally
    # -------------------------------------------------------
    out = eq(symbol)        # <-- your existing eq(symbol)
    print(out)
    if not isinstance(out, dict):
        return "<h3>Error: EQ data not available</h3>"

    # -------------------------------------------------------
    # Helper to convert DF → HTML table
    # -------------------------------------------------------
    def df_to_table(df):
        if df is None or len(df) == 0:
            return '<div class="empty">No data</div>'
        return df.to_html(index=False, escape=False, border=0, classes="tbl")

    # -------------------------------------------------------
    # ORDER — metadata FIRST (date table)
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

    # Normalize all values into DataFrame
    normalized = {}
    for sec in section_order:
        val = out.get(sec, None)
        if isinstance(val, pd.DataFrame):
            normalized[sec] = val
        elif isinstance(val, list):
            normalized[sec] = pd.DataFrame(val)
        elif isinstance(val, dict):
            normalized[sec] = pd.DataFrame([val])
        else:
            normalized[sec] = pd.DataFrame()

    # -------------------------------------------------------
    # Build sections HTML
    # -------------------------------------------------------
    section_html = ""
    for sec in section_order:
        df = normalized[sec]
        section_html += f"""
        <div class="section">
            <div class="section-header">
                <div class="section-title">{sec}</div>
                <button class="toggle-btn" onclick="toggleSection('{sec}')">View / Hide</button>
            </div>
            <div id="{sec}" class="section-body">
                {df_to_table(df)}
            </div>
        </div>
        """

    # -------------------------------------------------------
    # FINAL HTML PAGE
    # -------------------------------------------------------
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
        .section-body {{
            margin-top: 6px;
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
        if (e.style.display === "none") {{
            e.style.display = "block";
        }} else {{
            e.style.display = "none";
        }}
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
