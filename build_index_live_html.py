from nsepython import *
import pandas as pd

def build_index_live_html(name=""):
    p = nse_index_live(name)

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())

    if full_df.empty:
        main_df = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df = full_df.iloc[[0]]
        const_df = full_df.iloc[1:]
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]

    rem_html  = rem_df.to_html(index=False, escape=False)
    main_html = main_df.to_html(index=False, escape=False)
    cons_html = const_df.to_html(index=False, escape=False)

    # Metrics for matrix tables
    metric_cols = [
        "pchange", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d"
    ]

    metric_tables = ""

    for col in metric_cols:
        if col not in full_df.columns:
            continue

        df_small = full_df[["symbol", col]].copy()
        tbl = df_small.to_html(index=False)

        metric_tables += f"""
        <div class="small-table">
            <div class="st-title">symbol vs {col}</div>
            <div class="st-body">{tbl}</div>
        </div>
        """

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

table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
}}

th, td {{
    border: 1px solid #bbb;
    padding: 6px 8px;
    text-align: left;
}}

th {{
    background: #333;
    color: white;
}}

h2, h3 {{
    font-weight: 600;
}}

/* ===================== MATRIX TABLES ONLY ===================== */

.grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin-top: 20px;
}}

.small-table {{
    background: white;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    border: 1px solid #ddd;
}}

.small-table:hover {{
    transform: translateY(-3px);
    box-shadow: 0px 4px 10px rgba(0,0,0,0.20);
}}

.st-title {{
    font-size: 14px;
    text-align: center;
    margin-bottom: 10px;
    font-weight: bold;
    background: #222;
    color: white;
    padding: 4px 0;
    border-radius: 4px;
}}

.small-table table {{
    width: 100%;
    font-size: 12px;
    border: none;
}}

.small-table th {{
    background: #444;
    color: white;
    padding: 4px;
    font-size: 12px;
}}

.small-table td {{
    padding: 4px;
    border: 1px solid #ccc;
}}

</style>

</head>
<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<h3>Index Info (rem)</h3>
{rem_html}

<h3>Main Data (first row)</h3>
{main_html}

<h3>Constituents</h3>
{cons_html}

<h3>Compact Metric Tables (5-column matrix)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html
