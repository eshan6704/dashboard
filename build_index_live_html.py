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
        const_df = full_df.iloc[1:]  # Constituents
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]  # Remove first column
            if 'pChange' in const_df.columns:
                const_df['pChange'] = pd.to_numeric(const_df['pChange'], errors='coerce')
                const_df = const_df.sort_values('pChange', ascending=False)

    # ================= HELPER FUNCTION: COLOR-CODE NUMERIC =================
    def df_to_html_color(df):
        df_html = df.copy()
        for col in df_html.columns:
            if pd.api.types.is_numeric_dtype(df_html[col]):
                df_html[col] = df_html[col].apply(
                    lambda x: f'<span class="numeric-positive">{x}</span>' if x > 0 else
                              f'<span class="numeric-negative">{x}</span>' if x < 0 else str(x)
                )
        return df_html.to_html(index=False, escape=False, classes="compact-table")

    rem_html  = df_to_html_color(rem_df)
    main_html = df_to_html_color(main_df)
    cons_html = df_to_html_color(const_df)

    # ================= METRIC TABLES =================
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
        # Sort descending for better visibility
        df_const = df_const.sort_values(col, ascending=False)
        df_html = df_to_html_color(df_const[['symbol', col]])

        metric_tables += f"""
        <div class="small-table">
            <div class="st-title">{col}</div>
            <div class="st-body">{df_html}</div>
        </div>
        """

    # ================= FINAL HTML =================
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
body {{
    font-family: Arial;
    margin: 12px;
    background: #f5f5f5;
    color: #222;
    font-size: 14px;
}}

h2, h3 {{
    margin: 12px 0 6px 0;
    font-weight: 600;
}}

table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    border: 1px solid #bbb;
    padding: 5px 8px;
    text-align: left;
    font-size: 13px;
}}

th {{
    background: #333;
    color: white;
    font-weight: 600;
}}

.compact-table td.numeric-positive {{
    color: green;
    font-weight: bold;
}}
.compact-table td.numeric-negative {{
    color: red;
    font-weight: bold;
}}

.small-table {{
    background: white;
    border-radius: 6px;
    padding: 8px;
    box-shadow: 0px 1px 4px rgba(0,0,0,0.15);
    border: 1px solid #ddd;
    overflow: auto;
}}

.st-title {{
    font-size: 14px;
    text-align: center;
    margin-bottom: 6px;
    font-weight: bold;
    background: #222;
    color: white;
    padding: 5px 0;
    border-radius: 4px;
}}

.st-body {{
    max-height: 300px;  /* Scrollable if large */
    overflow: auto;
    font-size: 12px;
}}

.compact-section {{
    background: white;
    padding: 8px;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    border: 1px solid #ddd;
    margin-bottom: 15px;
    overflow-x: auto;
}}
</style>
</head>
<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<div class="compact-section">
    <h3>Index Info</h3>
    {rem_html}
</div>

<div class="compact-section">
    <h3>Main Data</h3>
    {main_html}
</div>

<div class="compact-section">
    <h3>Constituents</h3>
    {cons_html}
</div>

<h3>Metric Tables (All Symbols)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html
