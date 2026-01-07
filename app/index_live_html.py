from . import  nsepythonmodified as ns
import pandas as pd
from datetime import datetime as dt

# persist helpers (HF only)
from .persist import exists, load, save


def build_index_live_html(index_name ="NIFTY 50"):
    """
    Live HTML for NIFTY 50
    - Intraday TTL (15 minutes)
    - HTML only cache
    - persist.py controls validity
    """

    # ================= CACHE (TTL via persist) =================
    cache_name = "INTRADAY_INDEX_LIVE_NIFTY50"

    if exists(cache_name, "html"):
        cached_html = load(cache_name, "html")
        if isinstance(cached_html, str):
            return cached_html

    # ================= LIVE FETCH =================

    p = ns.nse_index_live(index_name)

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

            move_to_info = [c for c in ["segment", "equityTime", "preOpenTime"] if c in const_df.columns]
            if move_to_info:
                rem_df = pd.concat([rem_df, const_df[move_to_info].iloc[[0]]], axis=1)
                const_df = const_df.drop(columns=move_to_info)

            drop_cols_const = [
                "identifier","ffmc","stockIndClosePrice","lastUpdateTime",
                "chartTodayPath","chart30dPath","chart365dPath","series",
                "symbol_meta","activeSeries","debtSeries","isFNOSec",
                "isCASec","isSLBSec","isDebtSec","isSuspended",
                "tempSuspendedSeries","isETFSec","isDelisted",
                "slb_isin","isMunicipalBond","isHybridSymbol","QuotePreOpenFlag"
            ]
            const_df = const_df.drop(columns=[c for c in drop_cols_const if c in const_df.columns])

            drop_cols_main = [
                "series","symbol_meta","companyName","industry",
                "activeSeries","debtSeries","isFNOSec","isCASec",
                "isSLBSec","isDebtSec","isSuspended","tempSuspendedSeries",
                "isETFSec","isDelisted","isin","slb_isin","listingDate",
                "isMunicipalBond","isHybridSymbol",
                "segment","equityTime","preOpenTime","QuotePreOpenFlag"
            ]
            main_df = main_df.drop(columns=[c for c in drop_cols_main if c in main_df.columns])

            if "pChange" in const_df.columns:
                const_df["pChange"] = pd.to_numeric(const_df["pChange"], errors="coerce")
                const_df = const_df.sort_values("pChange", ascending=False)

    # ================= HTML HELPERS =================
    def format_number(val):
        """
        Format numeric values:
        - 0 => '0'
        - |val| < 0.001 => ±0.001
        - large numbers >= 1e7 => Crore format 'xx.xx Cr'
        - other => up to 3 decimals
        """
        if val == 0:
            return "0"
        # enforce minimum non-zero magnitude
        if abs(val) < 0.001:
            val_display = 0.001 if val > 0 else -0.001
            return f"{val_display:.3f}"

        # Crore formatting for large values
        if abs(val) >= 1e7:
            crores = val / 1e7
            return f"{crores:.2f} Cr"

        # normal numeric formatting with up to 3 decimals
        return f"{val:.3f}"

    def df_to_html_color(df, metric_col=None):
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
                # only handle numeric types
                if isinstance(val, (int, float)):
                    # format with the custom formatter
                    val_str = format_number(val)

                    # apply positive/negative classes
                    if val > 0:
                        cls = "numeric-positive"
                    elif val < 0:
                        cls = "numeric-negative"

                    # highlight top/bottom if metric
                    if metric_col and col == metric_col:
                        if idx in top_up:
                            cls += " top-up"
                        elif idx in top_down:
                            cls += " top-down"

                    df_html.at[idx, col] = f'<span class="{cls.strip()}">{val_str}</span>'
                else:
                    # leave text values untouched
                    df_html.at[idx, col] = str(val)

        return df_html.to_html(index=False, escape=False, classes="compact-table")

    def build_info_cards(rem_df, main_df):
        combined = pd.concat([rem_df, main_df], axis=1)
        combined = combined.loc[:, ~combined.columns.duplicated()]

        html = '<div class="mini-card-container">'
        for col in combined.columns:
            val = combined.at[0, col] if not combined.empty else ""
            html += f"""
            <div class="mini-card">
                <div class="card-key">{col}</div>
                <div class="card-val">{val}</div>
            </div>
            """
        html += "</div>"
        return html

    info_cards_html = build_info_cards(rem_df, main_df)
    cons_html = df_to_html_color(const_df)

    metric_cols = [
        "pChange","totalTradedValue","nearWKH",
        "nearWKL","perChange365d","perChange30d"
    ]

    metric_tables = ""
    for col in metric_cols:
        if col not in const_df.columns:
            continue
        df_m = const_df[["symbol", col]].copy()
        df_m[col] = pd.to_numeric(df_m[col], errors="coerce")
        df_m = df_m.sort_values(col, ascending=False)

        metric_tables += f"""
        <div class="small-table">
            <div class="st-title">{col}</div>
            <div class="st-body">{df_to_html_color(df_m, col)}</div>
        </div>
        """

    # ================= FINAL HTML =================
    html_out = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 12px; background: #f5f5f5; font-size: 14px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #bbb; padding: 5px 8px; }}
.numeric-positive {{ color: green; font-weight: bold; }}
.numeric-negative {{ color: red; font-weight: bold; }}
.top-up {{ background: #a8f0a5; }}
.top-down {{ background: #f0a8a8; }}

.mini-card-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
}}

.mini-card {{
    background: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    min-width: 130px;
    flex: 1 1 150px;
}}

.mini-card .card-key {{
    font-size: 12px;
    font-weight: bold;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

.mini-card .card-val {{
    font-size: 16px;
    font-weight: bold;
    color: #222;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
.small-table {{ background: white; padding: 8px; border-radius: 6px; }}
.st-title {{ background: #222; color: white; text-align: center; padding: 5px; }}
.st-body {{ max-height: 300px; overflow-y: auto; }}
</style>
</head>
<body>

<h3>Index Info</h3>
{info_cards_html}

<h3>Constituents</h3>
{cons_html}

<h3>Metric Tables</h3>
<div class="grid">
{metric_tables}
</div>

</body>
</html>
"""

    # ================= SAVE (HTML ONLY) =================
    save(cache_name, html_out, "html")

    return html_out
