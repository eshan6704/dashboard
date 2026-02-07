
from app.nse import nsepythonmodified as ns

import pandas as pd
import re
from datetime import datetime as dt



def build_preopen_html(key):
    """
    Build full Pre-Open HTML
    - Daily TTL (via persist.py)
    - HTML only cache
    """

    # ================= CACHE (TTL via persist) =================
    cache_name = f"DAILY_PREOPEN_{key.upper()}"



    # ================= FETCH DATA =================
    p = ns.nse_preopen(key)

    data_df = p["data"]
    rem_df  = p["rem"]

    main_df  = data_df.iloc[[0]] if not data_df.empty else pd.DataFrame()
    const_df = data_df.iloc[1:] if len(data_df) > 1 else pd.DataFrame()

    # ================= REMOVE PATTERN COLUMNS =================
    pattern_remove = re.compile(r"^(price_|buyQty_|sellQty_|iep_)\d+$")

    def remove_pattern_cols(df):
        if df is None or df.empty:
            return df
        return df[[c for c in df.columns if not pattern_remove.match(c)]]

    main_df  = remove_pattern_cols(main_df)
    const_df = remove_pattern_cols(const_df)
    rem_df   = remove_pattern_cols(rem_df)

    # ================= TABLE COLOR HELPER =================
    def df_to_html_color(df, metric_col=None):
        if df is None or df.empty:
            return "<i>No data</i>"

        df_html = df.copy()
        top_up, top_down = [], []

        if metric_col and metric_col in df_html.columns:
            col_num = pd.to_numeric(df_html[metric_col], errors="coerce").dropna()
            top_up = col_num.nlargest(3).index.tolist()
            top_down = col_num.nsmallest(3).index.tolist()

        for idx, row in df_html.iterrows():
            for col in df_html.columns:
                val = row[col]
                cls = ""
                if isinstance(val, (int, float)):
                    val_fmt = f"{val:.2f}"
                    if val > 0:
                        cls = "numeric-positive"
                    elif val < 0:
                        cls = "numeric-negative"
                    if metric_col and col == metric_col:
                        if idx in top_up:
                            cls += " top-up"
                        elif idx in top_down:
                            cls += " top-down"
                    df_html.at[idx, col] = f'<span class="{cls.strip()}">{val_fmt}</span>'
                else:
                    df_html.at[idx, col] = str(val)

        return df_html.to_html(index=False, escape=False, classes="compact-table")

    # ================= MINI INFO CARDS =================
    def build_info_cards(rem_df, main_df):
        combined = pd.concat([rem_df, main_df], axis=1)
        combined = combined.loc[:, ~combined.columns.duplicated()]
        combined = remove_pattern_cols(combined)

        html = '<div class="mini-card-container">'
        for col in combined.columns:
            val = combined.at[0, col] if not combined.empty else ""
            html += f"""
            <div class="mini-card">
                <div class="card-key">{col}</div>
                <div class="card-val">{val}</div>
            </div>
            """
        html += '</div>'
        return html

    info_cards_html = build_info_cards(rem_df, main_df)

    # ================= CONSTITUENTS TABLE =================
    cons_html = df_to_html_color(const_df)

    # ================= METRIC TABLES =================
    metric_cols_allowed = [
        "pChange",
        "totalTurnover",
        "marketCap",
        "totalTradedVolume"
    ]

    metric_tables = ""
    for col in metric_cols_allowed:
        if col in const_df.columns:
            df_m = const_df.copy()
            df_m[col] = pd.to_numeric(df_m[col], errors="coerce")
            df_m = df_m.sort_values(col, ascending=False)

            show_cols = ["symbol", col] if "symbol" in df_m.columns else [col]
            metric_tables += f"""
            <div class="small-table">
                <div class="st-title">{col}</div>
                <div class="st-body">
                    {df_to_html_color(df_m[show_cols], metric_col=col)}
                </div>
            </div>
            """

    # ================= FINAL HTML =================
    html_out = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: Arial; margin: 12px; background: #f5f5f5; font-size: 14px; }}
h2, h3 {{ margin: 10px 0; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #bbb; padding: 6px; font-size: 13px; }}
th {{ background: #333; color: #fff; }}
.numeric-positive {{ color: green; font-weight: bold; }}
.numeric-negative {{ color: red; font-weight: bold; }}
.top-up {{ background: #b6f2b6; }}
.top-down {{ background: #f2b6b6; }}
.grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
.small-table {{ background: #fff; padding: 8px; border-radius: 6px; border: 1px solid #ddd; }}
.st-title {{ text-align: center; font-weight: bold; background: #222; color: #fff; padding: 6px; }}
.st-body {{ max-height: 300px; overflow-y: auto; }}
.mini-card-container {{ display: flex; flex-wrap: wrap; gap: 10px; }}
.mini-card {{ background: #fff; padding: 8px 10px; border-radius: 6px; border: 1px solid #ddd; min-width: 120px; }}
.card-key {{ font-weight: bold; }}
</style>
</head>
<body>

<h2>Pre-Open Market — {key}</h2>

<h3>Info</h3>
{info_cards_html}

<h3>Constituents</h3>
{cons_html}

<h3>Key Metrics</h3>
<div class="grid">
{metric_tables}
</div>

</body>
</html>
"""

    # ================= SAVE (HTML ONLY) =================


    return html_out