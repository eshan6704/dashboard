from nsepython import *
import pandas as pd
import re
from datetime import datetime as dt

# persist helpers (ALREADY EXIST IN YOUR PROJECT)
from persist import exists, load, save


def build_preopen_html(key="NIFTY"):
    """
    Build full Pre-Open HTML with daily cache.
    If cached HTML exists for today → return it.
    Else → fetch, rebuild, save, return.
    """

    # ================= CACHE =================
    today = dt.now().strftime("%Y-%m-%d")
    cache_key = f"preopen_html_{key}"

    if exists(cache_key):
        cached = load(cache_key)
        if isinstance(cached, dict) and cached.get("date") == today:
            return cached.get("html")

    # ================= FETCH DATA =================
    p = nsefetch(f"https://www.nseindia.com/api/market-data-pre-open?key={key}")

    data_df = df_from_data(p.pop("data"))
    rem_df  = df_from_data([p])

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
        top3_up, top3_down = [], []

        if metric_col and metric_col in df_html.columns:
            if pd.api.types.is_numeric_dtype(df_html[metric_col]):
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

                    if col == metric_col:
                        if idx in top3_up:
                            style += " top-up"
                        elif idx in top3_down:
                            style += " top-down"

                    df_html.at[idx, col] = f'<span class="{style.strip()}">{val_fmt}</span>'
                else:
                    df_html.at[idx, col] = str(val)

        return df_html.to_html(index=False, escape=False, classes="compact-table")

    # ================= MINI CARDS =================
    def build_info_cards(rem_df, main_df):
        combined = pd.concat([rem_df, main_df], axis=1)
        combined = combined.loc[:, ~combined.columns.duplicated()]
        combined = remove_pattern_cols(combined)

        cards = '<div class="mini-card-container">'
        for col in combined.columns:
            val = combined.at[0, col] if not combined.empty else ""
            cards += f"""
            <div class="mini-card">
                <div class="card-key">{col}</div>
                <div class="card-val">{val}</div>
            </div>
            """
        cards += '</div>'
        return cards

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
        if col in const_df.columns and pd.api.types.is_numeric_dtype(const_df[col]):
            df_metric = const_df.copy()
            df_metric[col] = pd.to_numeric(df_metric[col], errors="coerce")
            df_metric = df_metric.sort_values(col, ascending=False)

            show_cols = ["symbol", col] if "symbol" in df_metric.columns else [col]
            metric_tables += f"""
            <div class="small-table">
                <div class="st-title">{col}</div>
                <div class="st-body">
                    {df_to_html_color(df_metric[show_cols], metric_col=col)}
                </div>
            </div>
            """

    # ================= FINAL HTML =================
    html = f"""
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
.compact-table td.numeric-positive {{ color: green; font-weight: bold; }}
.compact-table td.numeric-negative {{ color: red; font-weight: bold; }}
.compact-table td.top-up {{ background: #b6f2b6; }}
.compact-table td.top-down {{ background: #f2b6b6; }}
.grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
.small-table {{ background: #fff; padding: 8px; border-radius: 6px; border: 1px solid #ddd; }}
.st-title {{ text-align: center; font-weight: bold; background: #222; color: #fff; padding: 6px; border-radius: 4px; }}
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

    # ================= SAVE CACHE =================
    save(cache_key, {
        "date": today,
        "html": html
    })

    return html