from nsepython import *
import pandas as pd
import re

def build_preopen_html(key="NIFTY"):
    # Fetch pre-open data
    p = nsefetch(f"https://www.nseindia.com/api/market-data-pre-open?key={key}")
    data_df = df_from_data(p.pop("data"))
    rem_df  = df_from_data([p])
    
    main_df = data_df.iloc[[0]] if not data_df.empty else pd.DataFrame()
    const_df = data_df.iloc[1:] if len(data_df) > 1 else pd.DataFrame()
    
    # ================= REMOVE *_x AND SPECIFIC PATTERNS =================
    pattern_remove = re.compile(r"^(price_|buyQty_|sellQty_|iep_)\d+$")
    
    def remove_pattern_cols(df):
        return df[[c for c in df.columns if not pattern_remove.match(c)]]
    
    main_df = remove_pattern_cols(main_df)
    const_df = remove_pattern_cols(const_df)
    rem_df = remove_pattern_cols(rem_df)

    # ================= HELPER FUNCTION =================
    def df_to_html_color(df, metric_col=None):
        df_html = df.copy()
        top3_up, top3_down = [], []
        if metric_col and metric_col in df_html.columns and pd.api.types.is_numeric_dtype(df_html[metric_col]):
            col_numeric = df_html[metric_col].dropna()
            top3_up = col_numeric.nlargest(3).index.tolist()
            top3_down = col_numeric.nsmallest(3).index.tolist()

        for idx, row in df_html.iterrows():
            for col in df_html.columns:
                val = row[col]
                style = ""
                if isinstance(val, (int, float)):
                    val_fmt = f"{val:.2f}"
                    if val > 0:
                        style = "numeric-positive"
                    elif val < 0:
                        style = "numeric-negative"
                    if metric_col == col:
                        if idx in top3_up:
                            style += " top-up"
                        elif idx in top3_down:
                            style += " top-down"
                    df_html.at[idx, col] = f'<span class="{style.strip()}">{val_fmt}</span>'
                else:
                    df_html.at[idx, col] = str(val)
        return df_html.to_html(index=False, escape=False, classes="compact-table")

    # ================= MINI-CARDS =================
    def merge_info_main_cards(rem_df, main_df):
        combined = pd.concat([rem_df, main_df], axis=1)
        combined = combined.loc[:, ~combined.columns.duplicated()]
        # Remove pattern columns
        combined = combined[[c for c in combined.columns if not pattern_remove.match(c)]]
        cards_html = '<div class="mini-card-container">'
        for col in combined.columns:
            val = combined.at[0, col] if not combined.empty else ""
            cards_html += f'''
            <div class="mini-card">
                <div class="card-key">{col}</div>
                <div class="card-val">{val}</div>
            </div>
            '''
        cards_html += '</div>'
        return cards_html

    info_cards_html = merge_info_main_cards(rem_df, main_df)

    # ================= Constituents table =================
    cons_html = df_to_html_color(const_df) if not const_df.empty else "<i>No pre-open constituents</i>"

    # ================= Metric tables (restricted to selected columns) =================
    metric_cols_allowed = ["pChange", "totalTurnover", "marketCap", "totalTradedVolume"]
    metric_cols = [c for c in metric_cols_allowed if c in const_df.columns and pd.api.types.is_numeric_dtype(const_df[c])] if not const_df.empty else []

    metric_tables = ""
    for col in metric_cols:
        df_const = const_df.copy()
        df_const[col] = pd.to_numeric(df_const[col], errors="ignore")
        df_const = df_const.sort_values(col, ascending=False)
        df_html = df_to_html_color(df_const[['symbol', col]] if 'symbol' in df_const.columns else df_const[[col]], metric_col=col)
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
body {{ font-family: Arial; margin: 12px; background: #f5f5f5; color: #222; font-size: 14px; }}
h2, h3 {{ margin: 12px 0 6px 0; font-weight: 600; }}
table {{ border-collapse: collapse; width: 100%; table-layout: auto; }}
th, td {{ border: 1px solid #bbb; padding: 5px 8px; text-align: left; font-size: 13px; }}
th {{ background: #333; color: white; font-weight: 600; }}
.compact-table td.numeric-positive {{ color: green; font-weight: bold; }}
.compact-table td.numeric-negative {{ color: red; font-weight: bold; }}
.compact-table td.top-up {{ background: #a8f0a5; }}
.compact-table td.top-down {{ background: #f0a8a8; }}
.small-table {{ background: white; border-radius: 6px; padding: 8px; box-shadow: 0px 1px 4px rgba(0,0,0,0.15); border: 1px solid #ddd; overflow-y: auto; }}
.st-title {{ font-size: 14px; text-align: center; margin-bottom: 6px; font-weight: bold; background: #222; color: white; padding: 5px 0; border-radius: 4px; }}
.st-body {{ max-height: 300px; overflow-y: auto; font-size: 12px; }}
.grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 12px; }}
.mini-card-container {{ display: flex; flex-wrap: wrap; gap: 10px; }}
.mini-card {{ background: #fff; padding: 8px 10px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); min-width: 120px; font-size: 13px; }}
.card-key {{ font-weight: bold; color: #333; margin-bottom: 2px; }}
.card-val {{ color: #222; }}
</style>
</head>
<body>

<h2>Pre-Open Data: {key}</h2>

<div class="compact-section">
    <h3>Info + Main Data</h3>
    {info_cards_html}
</div>

<div class="compact-section">
    <h3>Pre-Open Constituents</h3>
    {cons_html}
</div>

<h3>Metric Tables (selected numeric)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html
