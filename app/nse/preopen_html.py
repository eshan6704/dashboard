from app.nse import nsepythonmodified as ns
import pandas as pd
import re
from datetime import datetime as dt


# ──────────────────────────────────────────────────────────────
#  SHARED STYLE  (identical navy theme to index live dashboard)
# ──────────────────────────────────────────────────────────────

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg-base:       #f0f4f9;
  --bg-panel:      #e6ecf5;
  --bg-card:       #ffffff;
  --bg-card-hover: #eaf0fa;
  --bg-row-alt:    #f5f8fd;
  --border:        #c8d6e8;
  --border-bright: #a0b8d8;

  --text-primary:  #0f2044;
  --text-muted:    #3a5a8a;
  --text-label:    #7a9bbf;

  --accent:        #1a56c4;
  --accent-dim:    #4a7de0;

  --up:            #0a8a4f;
  --up-bg:         rgba(10, 138, 79, 0.10);
  --up-bg-strong:  rgba(10, 138, 79, 0.20);
  --down:          #c0182e;
  --down-bg:       rgba(192, 24, 46, 0.08);
  --down-bg-strong:rgba(192, 24, 46, 0.18);

  --font-mono: 'IBM Plex Mono', monospace;
  --font-sans: 'IBM Plex Sans', sans-serif;
  --radius: 4px;
  --radius-lg: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body, .nse-root {
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 13px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── TOP NAV BAR ── */
.nse-topbar {
  background: linear-gradient(90deg, #0f2044 0%, #1a3a6e 100%);
  padding: 0 20px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.nse-topbar .nse-logo {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
}
.nse-topbar .nse-title  { color: #ffffff; }
.nse-topbar .nse-subtitle { color: rgba(255,255,255,0.5); }
.nse-topbar .nse-timestamp { color: rgba(255,255,255,0.45); }

/* ── PRE-OPEN BADGE ── */
.preopen-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(244,196,48,0.18);
  border: 1px solid rgba(244,196,48,0.35);
  color: #d4a800;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  padding: 3px 10px;
  border-radius: 20px;
  margin-left: 12px;
}
.preopen-badge::before {
  content: '';
  width: 6px; height: 6px;
  background: #d4a800;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

/* ── DASHBOARD WRAPPER ── */
.nse-root {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

/* ── HEADER-LEFT ── */
.nse-header-left { display: flex; align-items: center; gap: 14px; }
.nse-logo {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #1a56c4 0%, #0f2f7a 100%);
  border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-weight: 600; font-size: 14px;
  color: #fff; letter-spacing: -1px; flex-shrink: 0;
}
.nse-title {
  font-family: var(--font-mono); font-size: 18px; font-weight: 600;
  letter-spacing: 0.04em;
}
.nse-subtitle {
  font-family: var(--font-mono); font-size: 11px;
  color: rgba(255,255,255,0.5); letter-spacing: 0.08em; margin-top: 1px;
}
.nse-timestamp {
  font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em;
}
.nse-live-dot {
  display: inline-block; width: 7px; height: 7px;
  background: #d4a800; border-radius: 50%; margin-right: 6px;
  box-shadow: 0 0 6px #d4a800;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.35; }
}

/* ── SECTION LABELS ── */
.nse-section-label {
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 600;
  letter-spacing: 0.14em; color: var(--text-label);
  text-transform: uppercase;
  margin-bottom: 12px; padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

/* ── INFO CARD GRID ── */
.nse-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(155px, 1fr));
  gap: 10px;
  margin-bottom: 24px;
}
.nse-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 12px 14px;
  transition: border-color 0.15s, background 0.15s;
  position: relative; overflow: hidden;
}
.nse-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-dim), transparent);
  opacity: 0; transition: opacity 0.2s;
}
.nse-card:hover { border-color: var(--border-bright); background: var(--bg-card-hover); }
.nse-card:hover::before { opacity: 1; }
.nse-card-label {
  font-family: var(--font-mono); font-size: 9.5px; font-weight: 500;
  letter-spacing: 0.1em; color: var(--text-label);
  text-transform: uppercase; margin-bottom: 6px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.nse-card-value {
  font-family: var(--font-mono); font-size: 15px; font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.nse-card-value.positive { color: var(--up); }
.nse-card-value.negative { color: var(--down); }
.nse-card-value.neutral  { color: var(--accent); }

/* ── METRIC MINI-TABLES GRID ── */
.nse-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.nse-metric-card {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.nse-metric-title {
  font-family: var(--font-mono); font-size: 10px; font-weight: 600;
  letter-spacing: 0.12em; color: var(--text-muted);
  text-transform: uppercase; padding: 10px 14px;
  background: var(--bg-card); border-bottom: 1px solid var(--border);
}

/* ── TABLES ── */
.compact-table {
  width: 100%; border-collapse: collapse;
  font-family: var(--font-mono); font-size: 12px;
}
.compact-table thead tr {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.compact-table thead th {
  padding: 8px 10px; font-size: 9.5px; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--text-label); text-align: right; white-space: nowrap;
}
.compact-table thead th:first-child { text-align: left; }
.compact-table tbody tr {
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.compact-table tbody tr:nth-child(even) { background: var(--bg-row-alt); }
.compact-table tbody tr:hover { background: var(--bg-card-hover); }
.compact-table tbody tr:last-child { border-bottom: none; }
.compact-table tbody td {
  padding: 7px 10px; text-align: right;
  white-space: nowrap; color: var(--text-muted);
}
.compact-table tbody td:first-child {
  text-align: left; color: var(--text-primary); font-weight: 500;
}

/* ── CELL COLORING — plain text only, no rectangles ── */
.numeric-positive { color: var(--up)   !important; }
.numeric-negative { color: var(--down) !important; }
.top-up           { color: var(--up)   !important; font-weight: 700; }
.top-down         { color: var(--down) !important; font-weight: 700; }

/* ── TABLE SCROLL WRAPPER ── */
.table-scroll {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

/* ── DIVIDER ── */
.nse-divider {
  border: none; border-top: 1px solid var(--border); margin: 20px 0;
}
"""


# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────

_PATTERN_REMOVE  = re.compile(r"^(price_|buyQty_|sellQty_|iep_)\d+$")
_COLOR_COLS      = {"pChange", "perChange365d", "perChange30d", "nearWKH", "nearWKL"}
_METRIC_LABELS   = {
    "pChange":           "% Change",
    "totalTurnover":     "Total Turnover",
    "marketCap":         "Market Cap",
    "totalTradedVolume": "Traded Volume",
}
_NEUTRAL_CARDS   = {
    "lastPrice", "previousClose", "open", "finalPrice",
    "totalTradedVolume", "totalTurnover", "marketCap",
}


def _drop_pattern_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df[[c for c in df.columns if not _PATTERN_REMOVE.match(c)]]


def _is_pure_number(s) -> bool:
    try:
        float(s)
    except (ValueError, TypeError):
        return False
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", str(s).strip()))


def _fmt(val_str: str) -> str:
    val = float(val_str)
    if val == 0:
        return "0"
    if abs(val) < 0.001:
        val = 0.001 if val > 0 else -0.001
    if abs(val) >= 1e7:
        return f"{val / 1e7:.2f} Cr"
    if abs(val) >= 1e5:
        return f"{val:,.0f}"
    if abs(val) >= 1:
        return f"{val:,.2f}"
    return f"{val:.4f}"


def _df_to_html_color(df: pd.DataFrame, metric_col: str | None = None) -> str:
    """
    Render DataFrame as a styled HTML table.
    - pChange-family columns: plain green/red text.
    - All other numeric columns: plain formatted text, no color.
    - Top-3 rows in metric_col get bold colored text.
    """
    if df is None or df.empty:
        return "<i style='color:var(--text-label)'>No data</i>"

    df_html  = df.copy().astype(str)
    top_up, top_down = [], []

    if metric_col and metric_col in df.columns:
        col_num  = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        top_up   = col_num.nlargest(3).index.tolist()
        top_down = col_num.nsmallest(3).index.tolist()

    for idx, row in df_html.iterrows():
        for col in df_html.columns:
            val = row[col]
            if not _is_pure_number(val):
                df_html.at[idx, col] = val
                continue

            num_val = float(val)
            fmt_str = _fmt(val)
            is_color_col = col in _COLOR_COLS or col == metric_col

            if is_color_col:
                if idx in top_up:
                    cls = "top-up"
                elif idx in top_down:
                    cls = "top-down"
                elif num_val > 0:
                    cls = "numeric-positive"
                elif num_val < 0:
                    cls = "numeric-negative"
                else:
                    cls = ""
                df_html.at[idx, col] = f'<span class="{cls}">{fmt_str}</span>' if cls else fmt_str
            else:
                df_html.at[idx, col] = fmt_str

    return df_html.to_html(index=False, escape=False, classes="compact-table")


def _card(label: str, val) -> str:
    val_str = str(val) if val is not None else "—"
    val_cls = ""
    if _is_pure_number(val_str):
        num = float(val_str)
        if num > 0:
            val_cls = "positive"
        elif num < 0:
            val_cls = "negative"
        val_str = _fmt(val_str)
    elif label in _NEUTRAL_CARDS:
        val_cls = "neutral"

    return f"""
<div class="nse-card">
  <div class="nse-card-label">{label}</div>
  <div class="nse-card-value {val_cls}">{val_str}</div>
</div>"""


def _section(title: str, body: str) -> str:
    return f"""
<div>
  <div class="nse-section-label">{title}</div>
  {body}
</div>"""


# ──────────────────────────────────────────────────────────────
#  MAIN BUILDER
# ──────────────────────────────────────────────────────────────

def build_preopen_html(key: str) -> str:
    """
    Build a professional navy-themed HTML page for NSE Pre-Open market data.
    Daily TTL — persist.py controls cache validity.
    """
    now_str    = dt.now().strftime("%d %b %Y  %H:%M:%S")
    cache_name = f"DAILY_PREOPEN_{key.upper()}"  # noqa: F841 — used by persist.py

    # ── FETCH ────────────────────────────────────────────────
    p       = ns.nse_preopen(key)
    data_df = p["data"]
    rem_df  = p["rem"]

    main_df  = data_df.iloc[[0]] if not data_df.empty else pd.DataFrame()
    const_df = data_df.iloc[1:]  if len(data_df) > 1  else pd.DataFrame()

    main_df  = _drop_pattern_cols(main_df)
    const_df = _drop_pattern_cols(const_df)
    rem_df   = _drop_pattern_cols(rem_df)

    # ── SORT CONSTITUENTS by pChange ─────────────────────────
    if "pChange" in const_df.columns:
        const_df["pChange"] = pd.to_numeric(const_df["pChange"], errors="coerce")
        const_df = const_df.sort_values("pChange", ascending=False)

    # ── INFO CARDS ───────────────────────────────────────────
    combined_info = pd.concat([rem_df, main_df], axis=1)
    combined_info = combined_info.loc[:, ~combined_info.columns.duplicated()]
    combined_info = _drop_pattern_cols(combined_info)

    # top-bar pChange for header accent
    p_change_val = 0.0
    if "pChange" in combined_info.columns and not combined_info.empty:
        try:
            p_change_val = float(combined_info.at[combined_info.index[0], "pChange"])
        except Exception:
            pass
    direction_arrow = "▲" if p_change_val >= 0 else "▼"
    direction_color = "#00c97a" if p_change_val >= 0 else "#ff5a72"

    cards_html = '<div class="nse-cards-grid">'
    for col in combined_info.columns:
        val = combined_info.at[combined_info.index[0], col] if not combined_info.empty else "—"
        cards_html += _card(col, val)
    cards_html += "</div>"

    # ── CONSTITUENTS TABLE ───────────────────────────────────
    const_table_html = f"""
<div class="table-scroll">
  {_df_to_html_color(const_df)}
</div>"""

    # ── METRIC MINI-TABLES (25 rows each) ────────────────────
    metric_cards_html = '<div class="nse-metric-grid">'
    for col, label in _METRIC_LABELS.items():
        if col not in const_df.columns:
            continue
        df_m = const_df.copy()
        df_m[col] = pd.to_numeric(df_m[col], errors="coerce")
        df_m = df_m.sort_values(col, ascending=False).head(25)
        show_cols = ["symbol", col] if "symbol" in df_m.columns else [col]
        metric_cards_html += f"""
<div class="nse-metric-card">
  <div class="nse-metric-title">{label}</div>
  {_df_to_html_color(df_m[show_cols], metric_col=col)}
</div>"""
    metric_cards_html += "</div>"

    # ── ASSEMBLE ─────────────────────────────────────────────
    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Pre-Open — {key}</title>
<style>
{_CSS}
</style>
</head>
<body>

  <!-- ── TOP NAV BAR ── -->
  <div class="nse-topbar">
    <div class="nse-header-left">
      <div class="nse-logo">NSE</div>
      <div>
        <div class="nse-title">PRE-OPEN · {key.upper()}</div>
        <div class="nse-subtitle">MARKET DATA DASHBOARD</div>
      </div>
      <span class="preopen-badge">PRE-OPEN SESSION</span>
      <div style="font-family:var(--font-mono);font-size:18px;margin-left:8px;color:{direction_color};">
        {direction_arrow} {abs(p_change_val):.2f}%
      </div>
    </div>
    <div class="nse-timestamp">
      <span class="nse-live-dot"></span>
      {now_str}
    </div>
  </div>

  <div class="nse-root">

    <!-- ── INFO CARDS ── -->
    {_section("Session Summary", cards_html)}

    <hr class="nse-divider"/>

    <!-- ── CONSTITUENTS ── -->
    {_section("Constituents · Sorted by % Change", const_table_html)}

    <hr class="nse-divider"/>

    <!-- ── METRIC TABLES ── -->
    {_section("Key Metrics · Top 25", metric_cards_html)}

  </div>

</body>
</html>"""

    return html_out