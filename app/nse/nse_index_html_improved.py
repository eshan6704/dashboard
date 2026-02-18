from app.nse import nsepythonmodified as ns
import pandas as pd
from datetime import datetime as dt
import re


# ──────────────────────────────────────────────────────────────
#  STYLE CONSTANTS
# ──────────────────────────────────────────────────────────────

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg-base:       #0a0d12;
  --bg-panel:      #0f1318;
  --bg-card:       #141920;
  --bg-card-hover: #1a2230;
  --bg-row-alt:    #0d1017;
  --border:        #1e2a38;
  --border-bright: #263548;

  --text-primary:  #e8edf5;
  --text-muted:    #5a7490;
  --text-label:    #3d5a78;

  --accent:        #00b4d8;
  --accent-dim:    #00607a;

  --up:            #00d68f;
  --up-bg:         rgba(0, 214, 143, 0.08);
  --up-bg-strong:  rgba(0, 214, 143, 0.18);
  --down:          #ff4d6d;
  --down-bg:       rgba(255, 77, 109, 0.08);
  --down-bg-strong:rgba(255, 77, 109, 0.18);

  --gold:          #f4c430;
  --gold-bg:       rgba(244, 196, 48, 0.12);

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

/* ── DASHBOARD WRAPPER ── */
.nse-root {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

/* ── HEADER ── */
.nse-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.nse-header-left { display: flex; align-items: center; gap: 14px; }
.nse-logo {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--accent) 0%, #0077a8 100%);
  border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-weight: 600; font-size: 14px;
  color: #fff; letter-spacing: -1px;
}
.nse-title {
  font-family: var(--font-mono); font-size: 18px; font-weight: 600;
  letter-spacing: 0.04em; color: var(--text-primary);
}
.nse-subtitle {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-muted); letter-spacing: 0.08em; margin-top: 1px;
}
.nse-timestamp {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-label); letter-spacing: 0.06em;
}
.nse-live-dot {
  display: inline-block; width: 7px; height: 7px;
  background: var(--up); border-radius: 50%;
  margin-right: 6px;
  box-shadow: 0 0 6px var(--up);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

/* ── SECTION LABELS ── */
.nse-section-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--text-label);
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

/* ── INFO CARD GRID ── */
.nse-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
  margin-bottom: 24px;
}
.nse-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 12px 14px;
  transition: border-color 0.15s, background 0.15s;
  position: relative;
  overflow: hidden;
}
.nse-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-dim), transparent);
  opacity: 0;
  transition: opacity 0.2s;
}
.nse-card:hover { border-color: var(--border-bright); background: var(--bg-card-hover); }
.nse-card:hover::before { opacity: 1; }

.nse-card-label {
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 500;
  letter-spacing: 0.1em;
  color: var(--text-label);
  text-transform: uppercase;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nse-card-value {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nse-card-value.positive { color: var(--up); }
.nse-card-value.negative { color: var(--down); }
.nse-card-value.neutral  { color: var(--accent); }

/* ── TWO-COLUMN LAYOUT ── */
.nse-two-col {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  margin-bottom: 24px;
}
@media (max-width: 960px) {
  .nse-two-col { grid-template-columns: 1fr; }
}

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
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  text-transform: uppercase;
  padding: 10px 14px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}

/* ── TABLES ── */
.compact-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono);
  font-size: 12px;
}
.compact-table thead tr {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.compact-table thead th {
  padding: 8px 10px;
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-label);
  text-align: right;
  white-space: nowrap;
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
  padding: 7px 10px;
  text-align: right;
  white-space: nowrap;
  color: var(--text-muted);
}
.compact-table tbody td:first-child {
  text-align: left;
  color: var(--text-primary);
  font-weight: 500;
}

/* ── CELL COLORING ── */
.numeric-positive {
  color: var(--up) !important;
  background: var(--up-bg);
  border-radius: 2px;
  padding: 1px 4px;
}
.numeric-negative {
  color: var(--down) !important;
  background: var(--down-bg);
  border-radius: 2px;
  padding: 1px 4px;
}
.top-up {
  background: var(--up-bg-strong) !important;
  font-weight: 600;
}
.top-down {
  background: var(--down-bg-strong) !important;
  font-weight: 600;
}
.badge-up {
  display: inline-block;
  background: var(--up-bg-strong);
  color: var(--up);
  border: 1px solid rgba(0,214,143,0.25);
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 11px;
  font-weight: 600;
}
.badge-down {
  display: inline-block;
  background: var(--down-bg-strong);
  color: var(--down);
  border: 1px solid rgba(255,77,109,0.25);
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 11px;
  font-weight: 600;
}

/* ── SCROLLABLE TABLE WRAPPER ── */
.table-scroll {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

/* ── DIVIDER ── */
.nse-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 20px 0;
}
"""

_JS = """
document.querySelectorAll('.compact-table tbody td').forEach(td => {
  const span = td.querySelector('span');
  if (!span) return;
  const val = parseFloat(span.textContent);
  if (!isNaN(val)) {
    td.style.textAlign = 'right';
  }
});
"""


# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────

def _is_pure_number(s) -> bool:
    try:
        float(s)
    except (ValueError, TypeError):
        return False
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", str(s).strip()))


def _fmt(val_str: str) -> str:
    """Format a pure-numeric string for display."""
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


def _classify(num_val: float, col: str | None, idx, top_up: list, top_down: list) -> str:
    cls_parts = []
    if num_val > 0:
        cls_parts.append("numeric-positive")
    elif num_val < 0:
        cls_parts.append("numeric-negative")
    if col and idx in top_up:
        cls_parts.append("top-up")
    elif col and idx in top_down:
        cls_parts.append("top-down")
    return " ".join(cls_parts)


def _df_to_html_color(df: pd.DataFrame, metric_col: str | None = None) -> str:
    """Convert DataFrame to a styled HTML table."""
    df_html = df.copy().astype(str)
    top_up, top_down = [], []

    if metric_col and metric_col in df.columns:
        col_num = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        top_up   = col_num.nlargest(3).index.tolist()
        top_down = col_num.nsmallest(3).index.tolist()

    for idx, row in df_html.iterrows():
        for col in df_html.columns:
            val = row[col]
            if _is_pure_number(val):
                num_val  = float(val)
                fmt_str  = _fmt(val)
                cls      = _classify(num_val, metric_col, idx, top_up, top_down)
                cell_cls = f' class="{cls}"' if cls else ""
                df_html.at[idx, col] = f"<span{cell_cls}>{fmt_str}</span>"
            else:
                df_html.at[idx, col] = val

    return df_html.to_html(index=False, escape=False, classes="compact-table")


def _card(label: str, val, up_fields=(), down_fields=()) -> str:
    """Render a single info card."""
    val_str = str(val) if val is not None else "—"
    val_cls = ""
    if label in up_fields or (
        _is_pure_number(val_str) and float(val_str) > 0
    ):
        val_cls = "positive"
    elif label in down_fields or (
        _is_pure_number(val_str) and float(val_str) < 0
    ):
        val_cls = "negative"
    elif label in ("lastPrice", "previousClose", "open", "intraDayHighLow",
                   "weekHighLow", "totalTradedVolume", "totalTradedValue"):
        val_cls = "neutral"
    if _is_pure_number(val_str):
        val_str = _fmt(val_str)

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

METRIC_LABELS = {
    "pChange":          "% Change",
    "totalTradedValue": "Traded Value",
    "nearWKH":          "Near 52W High",
    "nearWKL":          "Near 52W Low",
    "perChange365d":    "1Y Change %",
    "perChange30d":     "30D Change %",
}


def build_index_live_html(index_name: str = "NIFTY 50") -> str:
    """
    Build a professional Bloomberg-terminal-style HTML page for a live NSE index.

    Intraday TTL (15 minutes) — persist.py controls cache validity.
    """
    now_str = dt.now().strftime("%d %b %Y  %H:%M:%S")

    # ── LIVE FETCH ──────────────────────────────────────────
    p        = ns.nse_index_live(index_name)
    full_df  = p.get("data", pd.DataFrame())
    rem_df   = p.get("rem",  pd.DataFrame())

    if full_df.empty:
        main_df  = pd.DataFrame()
        const_df = pd.DataFrame()
    else:
        main_df  = full_df.iloc[[0]]
        const_df = full_df.iloc[1:].copy()
        if not const_df.empty:
            const_df = const_df.iloc[:, 1:]

    # move segment/time columns to info strip
    move_cols = [c for c in ("segment", "equityTime", "preOpenTime") if c in const_df.columns]
    if move_cols:
        rem_df   = pd.concat([rem_df, const_df[move_cols].iloc[[0]]], axis=1)
        const_df = const_df.drop(columns=move_cols)

    # drop noise columns
    _DROP_CONST = {
        "identifier", "ffmc", "stockIndClosePrice", "lastUpdateTime",
        "chartTodayPath", "chart30dPath", "chart365dPath", "series",
        "symbol_meta", "activeSeries", "debtSeries", "isFNOSec",
        "isCASec", "isSLBSec", "isDebtSec", "isSuspended",
        "tempSuspendedSeries", "isETFSec", "isDelisted",
        "slb_isin", "isMunicipalBond", "isHybridSymbol", "QuotePreOpenFlag",
    }
    _DROP_MAIN = {
        "series", "symbol_meta", "companyName", "industry",
        "activeSeries", "debtSeries", "isFNOSec", "isCASec",
        "isSLBSec", "isDebtSec", "isSuspended", "tempSuspendedSeries",
        "isETFSec", "isDelisted", "isin", "slb_isin", "listingDate",
        "isMunicipalBond", "isHybridSymbol",
        "segment", "equityTime", "preOpenTime", "QuotePreOpenFlag",
    }
    const_df = const_df.drop(columns=[c for c in _DROP_CONST if c in const_df.columns])
    main_df  = main_df.drop( columns=[c for c in _DROP_MAIN  if c in main_df.columns])

    # sort constituents
    if "pChange" in const_df.columns:
        const_df["pChange"] = pd.to_numeric(const_df["pChange"], errors="coerce")
        const_df = const_df.sort_values("pChange", ascending=False)

    # ── INFO CARDS ──────────────────────────────────────────
    combined_info = pd.concat([rem_df, main_df], axis=1)
    combined_info = combined_info.loc[:, ~combined_info.columns.duplicated()]

    # Detect overall direction for header accent
    p_change_val = 0.0
    if "pChange" in combined_info.columns and not combined_info.empty:
        try:
            p_change_val = float(combined_info.at[combined_info.index[0], "pChange"])
        except Exception:
            pass
    direction_cls   = "positive" if p_change_val >= 0 else "negative"
    direction_arrow = "▲" if p_change_val >= 0 else "▼"

    cards_html = '<div class="nse-cards-grid">'
    for col in combined_info.columns:
        val = combined_info.at[combined_info.index[0], col] if not combined_info.empty else "—"
        cards_html += _card(col, val)
    cards_html += "</div>"

    # ── CONSTITUENTS TABLE ──────────────────────────────────
    const_table_html = f"""
<div class="table-scroll">
  {_df_to_html_color(const_df)}
</div>"""

    # ── METRIC MINI-TABLES ──────────────────────────────────
    metric_cards_html = '<div class="nse-metric-grid">'
    for col, label in METRIC_LABELS.items():
        if col not in const_df.columns:
            continue
        df_m = const_df[["symbol", col]].copy()
        df_m[col] = pd.to_numeric(df_m[col], errors="coerce")
        df_m = df_m.sort_values(col, ascending=False).head(10)
        metric_cards_html += f"""
<div class="nse-metric-card">
  <div class="nse-metric-title">{label}</div>
  {_df_to_html_color(df_m, col)}
</div>"""
    metric_cards_html += "</div>"

    # ── ASSEMBLE ─────────────────────────────────────────────
    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{index_name} · Live Dashboard</title>
<style>
{_CSS}
</style>
</head>
<body>
<div class="nse-root">

  <!-- ── HEADER ── -->
  <div class="nse-header">
    <div class="nse-header-left">
      <div class="nse-logo">NSE</div>
      <div>
        <div class="nse-title">{index_name}</div>
        <div class="nse-subtitle">LIVE MARKET DASHBOARD</div>
      </div>
      <div class="nse-card-value {direction_cls}" style="font-family:var(--font-mono);font-size:20px;margin-left:12px;">
        {direction_arrow} {abs(p_change_val):.2f}%
      </div>
    </div>
    <div class="nse-timestamp">
      <span class="nse-live-dot"></span>
      {now_str}
    </div>
  </div>

  <!-- ── INFO CARDS ── -->
  {_section("Index Summary", cards_html)}

  <hr class="nse-divider"/>

  <!-- ── CONSTITUENTS ── -->
  {_section("Constituents · Sorted by % Change", const_table_html)}

  <hr class="nse-divider"/>

  <!-- ── METRIC TABLES ── -->
  {_section("Performance Metrics", metric_cards_html)}

</div>
<script>
{_JS}
</script>
</body>
</html>"""

    return html_out
