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
        const_df = full_df.iloc[1:]           # Constituents
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]   # Remove first column

    rem_html  = rem_df.to_html(index=False, escape=False)
    main_html = main_df.to_html(index=False, escape=False)
    cons_html = const_df.to_html(index=False, escape=False)

    # ==========================================================
    # METRICS WITH TOP 20 UPSIDE + TOP 20 DOWNSIDE
    # ==========================================================

    metric_cols = [
        "pChange", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d", "perChange30d", "listingDate"
    ]

    metric_tables = ""

    for col in metric_cols:
        if col not in const_df.columns:
            continue

        df_const = const_df.copy()
        df_const[col] = pd.to_numeric(df_const[col], errors="ignore")

        # Top 20 Upside
        df_up = df_const[["symbol", col]].dropna().sort_values(col, ascending=False).head(20)
        tbl_up = df_up.to_html(index=False)

        # Top 20 Downside
        df_down = df_const[["symbol", col]].dropna().sort_values(col, ascending=True).head(20)
        tbl_down = df_down.to_html(index=False)

        metric_tables += f"""
        <div class="small-table">

            <div class="st-title">{col}</div>

            <div class="sub-title up">Top 20 Upside</div>
            <div class="st-body">{tbl_up}</div>

            <div class="sub-title down">Top 20 Downside</div>
            <div class="st-body">{tbl_down}</div>

        </div>
        """

    # ==========================================================
    # FINAL HTML
    # ==========================================================

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

/* GRID LAYOUT */
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
    border: 1px solid #ddd;
}}

.st-title {{
    font-size: 15px;
    text-align: center;
    margin-bottom: 10px;
    font-weight: bold;
    background: #222;
    color: white;
    padding: 6px 0;
    border-radius: 4px;
}}

.sub-title {{
    margin-top: 10px;
    font-weight: bold;
    text-align: center;
    padding: 5px;
    border-radius: 4px;
    font-size: 13px;
    color: white;
}}

.sub-title.up {{
    background: #0a4;   /* Green */
}}

.sub-title.down {{
    background: #c22;   /* Red */
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

<h3>Metric Tables (Top 20 Upside / Downside)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""

    return html
