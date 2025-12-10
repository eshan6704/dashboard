
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

            # Columns to move from constituents to info
            move_to_info = [c for c in ['segment', 'equityTime', 'preOpenTime'] if c in const_df.columns]
            if move_to_info:
                rem_df = pd.concat([rem_df, const_df[move_to_info].iloc[[0]]], axis=1)
                const_df = const_df.drop(columns=move_to_info)

            # Drop unnecessary columns from Constituents
            drop_cols_const = [
                "identifier", "ffmc", "stockIndClosePrice", "lastUpdateTime",
                "chartTodayPath", "chart30dPath", "chart365dPath", "series",
                "symbol_meta", "activeSeries", "debtSeries", "isFNOSec",
                "isCASec", "isSLBSec", "isDebtSec", "isSuspended",
                "tempSuspendedSeries", "isETFSec", "isDelisted",
                "slb_isin", "isMunicipalBond", "isHybridSymbol", "QuotePreOpenFlag"
            ]
            const_df = const_df.drop(columns=[c for c in drop_cols_const if c in const_df.columns])

            # Drop unnecessary columns from Main Data
            drop_cols_main = [
                "series", "symbol_meta", "companyName", "industry", "activeSeries", "debtSeries",
                "isFNOSec", "isCASec", "isSLBSec", "isDebtSec", "isSuspended", "tempSuspendedSeries",
                "isETFSec", "isDelisted", "isin", "slb_isin", "listingDate", "isMunicipalBond",
                "isHybridSymbol", "segment", "equityTime", "preOpenTime", "QuotePreOpenFlag"
            ]
            main_df = main_df.drop(columns=[c for c in drop_cols_main if c in main_df.columns])

            # Ensure pChange is numeric and sort
            if 'pChange' in const_df.columns:
                const_df['pChange'] = pd.to_numeric(const_df['pChange'], errors='coerce')
                const_df = const_df.sort_values('pChange', ascending=False)

    # ================= HELPER FUNCTION: COLOR-CODE AND FORMAT NUMERIC =================
    def df_to_html_color(df, metric_col=None):
        df_html = df.copy()
        top3_up = []
        top3_down = []
        if metric_col and metric_col in df_html.columns and pd.api.types.is_numeric_dtype(df_html[metric_col]):
            col_numeric = df_html[metric_col].dropna()
            top3_up = col_numeric.nlargest(3).index.tolist()
            top3_down = col_numeric.nsmallest(3).index.tolist()

        for idx, row in df_html.iterrows():
            for col in df_html.columns:
                val = row[col]
                style = ""
                if pd.api.types.is_numeric_dtype(type(val)) or isinstance(val, (int, float)):
                    val_fmt = f"{val:.2f}"
                    if val > 0:
                        style = "numeric-positive"
                    elif val < 0:
                        style = "numeric-negative"
                    if metric_col and col == metric_col:
                        if idx in top3_up:
                            style += " top-up"
                        elif idx in top3_down:
                            style += " top-down"
                    df_html.at[idx, col] = f'<span class="{style.strip()}">{val_fmt}</span>'
                else:
                    df_html.at[idx, col] = str(val)
        return df_html.to_html(index=False, escape=False, classes="compact-table")

    # ================= MERGE INFO AND MAIN KEYS INTO MINI CARDS =================
    def merge_info_main_cards(rem_df, main_df):
        combined = pd.concat([rem_df, main_df], axis=1)
        # Remove duplicate columns
        combined = combined.loc[:, ~combined.columns.duplicated()]
        # Generate mini cards
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

    cons_html = df_to_html_color(const_df)

    # ================= METRIC TABLES =================
    metric_cols = [
        "pChange", "totalTradedValue", "nearWKH", "nearWKL",
        "perChange365d", "perChange30d"
    ]

    metric_tables = ""
    for col in metric_cols:
        if col not in const_df.columns:
            continue

        df_const = const_df.copy()
        df_const[col] = pd.to_numeric(df_const[col], errors="ignore")
        df_const = df_const.sort_values(col, ascending=False)
        df_html = df_to_html_color(df_const[['symbol', col]], metric_col=col)

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
    table-layout: auto;
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

/* Highlight top 3 gainers / losers */
.compact-table td.top-up {{
    background: #a8f0a5; /* light green */
}}
.compact-table td.top-down {{
    background: #f0a8a8; /* light red */
}}

/* Fixed row height & clipping for Constituent Table */
#constituents-table tr, #constituents-table td {{
    max-height: 25px;
    height: 25px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}}

.small-table {{
    background: white;
    border-radius: 6px;
    padding: 8px;
    box-shadow: 0px 1px 4px rgba(0,0,0,0.15);
    border: 1px solid #ddd;
    overflow-y: auto;
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
    max-height: 300px;  /* vertical scroll for metric tables */
    overflow-y: auto;
    font-size: 12px;
}}

.compact-section {{
    background: white;
    padding: 8px;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    border: 1px solid #ddd;
    margin-bottom: 15px;
    overflow-x: visible;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 12px;
}}

/* Mini cards for info + main */
.mini-card-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}}
.mini-card {{
    background: #fff;
    padding: 8px 10px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    min-width: 120px;
    font-size: 13px;
}}
.card-key {{
    font-weight: bold;
    color: #333;
    margin-bottom: 2px;
}}
.card-val {{
    color: #222;
}}
</style>
</head>
<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<div class="compact-section">
    <h3>Index Info + Main Data</h3>
    {info_cards_html}
</div>

<div class="compact-section">
    <h3>Constituents</h3>
    <div id="constituents-table">
        {cons_html}
    </div>
</div>

<h3>Metric Tables (All Symbols)</h3>
<div class="grid">
    {metric_tables}
</div>

</body>
</html>
"""
    return html
