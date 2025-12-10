import json
import pandas as pd
from nsepython import *
import html


def build_indices_html():
    """
    Generate a single, fully-rendered HTML string (no <script>) containing:
      - main indices table
      - dates table (if present)
      - one table per category/key
      - for each index record, a chart grid with 3 iframes (if paths exist) or placeholders

    Requires: indices() function available in scope which returns dict with keys:
      - "data": DataFrame of records (each row a dict with fields including at least 'key', 'index', 'indexSymbol')
      - "dates": DataFrame (optional)
    """
    p = indices()  # must exist in your module
    data_df = p.get("data", pd.DataFrame())
    dates_df = p.get("dates", pd.DataFrame())

    # Convert records to list of dicts for iteration
    records = data_df.to_dict(orient="records") if not data_df.empty else []

    # Hidden columns we don't want to show in per-category tables
    hidden_cols = {
        "key","chartTodayPath","chart30dPath","chart30Path","chart365dPath",
        "date365dAgo","date30dAgo","previousDay","oneWeekAgo","oneMonthAgoVal",
        "oneWeekAgoVal","oneYearAgoVal","index","indicativeClose"
    }

    def build_table_from_records(recs, cols=None):
        """Return HTML <table> string for recs (list of dicts). If cols provided, use that order."""
        if not recs:
            return "<p>No data available.</p>"

        # Determine columns
        if cols is None:
            # union of keys preserving insertion order from first record
            cols = []
            for r in recs:
                for k in r.keys():
                    if k not in cols:
                        cols.append(k)

        # Build header
        header_cells = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols)
        rows_html = []
        for r in recs:
            row_cells = []
            for c in cols:
                v = r.get(c, "")
                # Convert lists/dicts to string
                if isinstance(v, (list, dict)):
                    cell = html.escape(str(v))
                else:
                    cell = html.escape("" if v is None else str(v))
                row_cells.append(f"<td>{cell}</td>")
            rows_html.append("<tr>" + "".join(row_cells) + "</tr>")

        table_html = "<table>\n<thead>\n<tr>" + header_cells + "</tr>\n</thead>\n<tbody>\n" + "\n".join(rows_html) + "\n</tbody>\n</table>"
        return table_html

    def build_chart_grid_for_record(r):
        """
        Build a 3-panel grid for charts for a single record r.
        Uses r.get('chartTodayPath'), r.get('chart30dPath' or 'chart30Path'), r.get('chart365dPath').
        If a path is missing, show a placeholder box with text.
        """
        def iframe_or_placeholder(src, label):
            if src and isinstance(src, str) and src.strip():
                # escape src only in attribute context
                return f'<div class="chart-cell"><iframe src="{html.escape(src)}" frameborder="0" loading="lazy" title="{html.escape(label)}" style="width:100%;height:100%;"></iframe></div>'
            else:
                return f'<div class="chart-cell placeholder"><div class="ph-inner">{html.escape(label)}<br/>(no chart)</div></div>'

        today_src = r.get("chartTodayPath") or r.get("chartToday") or ""
        month30_src = r.get("chart30dPath") or r.get("chart30Path") or r.get("chart30") or ""
        year365_src = r.get("chart365dPath") or r.get("chart365Path") or r.get("chart365") or ""

        idx_name = r.get("index") or r.get("indexSymbol") or r.get("symbol") or ""

        grid = (
            '<div class="chart-grid-record">\n'
            f'  <div class="chart-header"><strong>{html.escape(str(idx_name))}</strong></div>\n'
            '  <div class="chart-row">\n'
            f'    {iframe_or_placeholder(today_src, "Today Chart")}\n'
            f'    {iframe_or_placeholder(month30_src, "30d Chart")}\n'
            '  </div>\n'
            '  <div class="chart-row">\n'
            f'    {iframe_or_placeholder(year365_src, "365d Chart")}\n'
            '  </div>\n'
            '</div>\n'
        )
        return grid

    # Build main full table (all columns present in records)
    main_table_html = build_table_from_records(records)

    # Build dates table if dates_df present
    dates_table_html = ""
    if not dates_df.empty:
        dates_records = dates_df.to_dict(orient="records")
        dates_table_html = build_table_from_records(dates_records)

    # Group records by 'key' (category)
    from collections import defaultdict
    groups = defaultdict(list)
    for r in records:
        k = r.get("key") or "UNCLASSIFIED"
        groups[k].append(r)

    # Build per-key tables and per-record chart grids
    per_key_sections = []
    for key_name, recs in groups.items():
        # Columns to show: all keys from first record except hidden_cols, preserving order
        first = recs[0] if recs else {}
        cols = [c for c in first.keys() if c not in hidden_cols]
        # But ensure some useful order: indexSymbol/index/name first if present
        preferred = ["indexSymbol","index","symbol","name"]
        cols_sorted = []
        for p in preferred:
            if p in cols:
                cols_sorted.append(p)
        for c in cols:
            if c not in cols_sorted:
                cols_sorted.append(c)

        table_html = build_table_from_records(recs, cols_sorted)
        # Build chart block for all recs in this key
        charts_html = "\n".join(build_chart_grid_for_record(r) for r in recs)

        section_html = f"""
        <section class="key-section">
          <h3>Category: {html.escape(str(key_name))} (Total: {len(recs)})</h3>
          <div class="key-table">{table_html}</div>
          <div class="key-charts">{charts_html}</div>
        </section>
        """
        per_key_sections.append(section_html)

    # CSS for layout (no JS)
    css = """
    <style>
    body { font-family: Arial, sans-serif; padding: 16px; color: #111; background: #fff; }
    h1,h2,h3 { color: #0b69a3; margin: 8px 0; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 12px; font-size: 13px; }
    th, td { border: 1px solid #d0d0d0; padding: 6px 8px; text-align: left; vertical-align: top; }
    th { background: #007bff; color: #fff; position: sticky; top: 0; z-index: 2; }
    .scroll { max-height: 420px; overflow: auto; border: 1px solid #eee; padding: 8px; background: #fafafa; margin-bottom: 18px; }
    .key-section { margin-bottom: 28px; padding: 8px 6px; border: 1px solid #e6eef6; background: #fbfeff; border-radius: 6px; }
    .chart-grid-record { border: 1px solid #e0e0e0; padding: 6px; margin: 8px 0; border-radius: 6px; background: #fff; }
    .chart-header { margin-bottom: 6px; }
    .chart-row { display: flex; gap: 8px; margin-bottom: 8px; }
    .chart-cell { flex: 1 1 0; height: 200px; border: 1px solid #ddd; }
    .chart-cell.iframe-wrap iframe { width:100%; height:100%; border:0; }
    .placeholder { display:flex; align-items:center; justify-content:center; background:#f6f6f6; color:#666; font-size:13px; }
    .ph-inner { text-align:center; padding:8px; }
    .meta { font-size: 13px; color: #444; margin-bottom: 8px; }
    </style>
    """

    # HTML assembly
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html><head><meta charset='utf-8'><title>NSE Indices (Static)</title>")
    html_parts.append(css)
    html_parts.append("</head><body>")
    html_parts.append("<h1>NSE Indices — Full Static Render</h1>")
    html_parts.append(f"<div class='meta'>Generated: {html.escape(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))}</div>")

    html_parts.append("<h2>Main Indices Table</h2>")
    html_parts.append("<div class='scroll'>")
    html_parts.append(main_table_html)
    html_parts.append("</div>")

    if dates_table_html:
        html_parts.append("<h2>Dates / Meta</h2>")
        html_parts.append("<div class='scroll'>")
        html_parts.append(dates_table_html)
        html_parts.append("</div>")

    html_parts.append("<h2>Categories & Charts (All)</h2>")
    html_parts.extend(per_key_sections)

    html_parts.append("</body></html>")

    return "\n".join(html_parts)
