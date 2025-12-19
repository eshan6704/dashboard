import json
import pandas as pd
from nsepython import *
import html
from datetime import datetime as dt
from collections import defaultdict

# persist helpers (already exist in your project)
from persist import exists, load, save


def build_indices_html():
    """
    Generate HTML:
      - main table
      - dates table
      - tables for all categories
      - charts ONLY for key == "INDICES ELIGIBLE IN DERIVATIVES"
      - flexible chart layout (no grid, auto-fit)
      - DAILY CACHE ENABLED
    """

    # ================= CACHE =================
    today = dt.now().strftime("%Y-%m-%d")
    cache_key = "indices_html"

    if exists(cache_key):
        cached = load(cache_key)
        if isinstance(cached, dict) and cached.get("date") == today:
            return cached.get("html")

    # ================= FETCH DATA =================
    p = indices()  # your existing function
    data_df = p.get("data", pd.DataFrame())
    dates_df = p.get("dates", pd.DataFrame())

    records = data_df.to_dict(orient="records") if not data_df.empty else []

    # Columns to hide in category tables
    hidden_cols = {
        "key","chartTodayPath","chart30dPath","chart30Path","chart365dPath",
        "date365dAgo","date30dAgo","previousDay","oneWeekAgo","oneMonthAgoVal",
        "oneWeekAgoVal","oneYearAgoVal","index","indicativeClose"
    }

    # ----------- BASIC TABLE BUILDER -----------
    def build_table_from_records(recs, cols=None):
        if not recs:
            return "<p>No data available.</p>"

        if cols is None:
            cols = []
            for r in recs:
                for k in r.keys():
                    if k not in cols:
                        cols.append(k)

        header = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols)

        body_rows = []
        for r in recs:
            tds = []
            for c in cols:
                v = r.get(c, "")
                if isinstance(v, (list, dict)):
                    v = str(v)
                tds.append(f"<td>{html.escape('' if v is None else str(v))}</td>")
            body_rows.append("<tr>" + "".join(tds) + "</tr>")

        return f"""
        <table>
            <thead><tr>{header}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
        </table>
        """

    # ----------- FLEXIBLE CHART BLOCK -----------
    def build_chart_grid_for_record(r):

        def iframe_if_exists(src, label):
            if src and isinstance(src, str) and src.strip():
                return f"""
                <div class="chart-flex-item">
                    <iframe src="{html.escape(src)}" loading="lazy"
                            frameborder="0" title="{html.escape(label)}"></iframe>
                </div>
                """
            return ""

        today_src   = r.get("chartTodayPath")  or r.get("chartToday")  or ""
        month30_src = r.get("chart30dPath")    or r.get("chart30Path") or ""
        year365_src = r.get("chart365dPath")   or r.get("chart365")   or ""

        block = (
            iframe_if_exists(today_src, "Today Chart") +
            iframe_if_exists(month30_src, "30d Chart") +
            iframe_if_exists(year365_src, "365d Chart")
        )

        if not block.strip():
            return ""

        title = r.get("index") or r.get("indexSymbol") or r.get("symbol") or ""

        return f"""
        <div class="chart-flex-block">
            <div class="chart-title"><strong>{html.escape(str(title))}</strong></div>
            <div class="chart-flex-container">
                {block}
            </div>
        </div>
        """

    # ----------- MAIN TABLE -----------
    main_table_html = build_table_from_records(records)

    # ----------- DATES TABLE -----------
    dates_table_html = ""
    if not dates_df.empty:
        dates_table_html = build_table_from_records(
            dates_df.to_dict(orient="records")
        )

    # ----------- GROUP BY KEY ----------
    groups = defaultdict(list)
    for r in records:
        groups[r.get("key") or "UNCLASSIFIED"].append(r)

    per_key_sections = []

    # ----------- PER CATEGORY SECTIONS ----------
    for key_name, recs in groups.items():

        first = recs[0]
        cols = [c for c in first.keys() if c not in hidden_cols]

        preferred = ["indexSymbol", "index", "symbol", "name"]
        ordered = [c for c in preferred if c in cols] + [c for c in cols if c not in preferred]

        table_html = build_table_from_records(recs, ordered)

        # Charts only for derivative-eligible indices
        if str(key_name).strip().upper() == "INDICES ELIGIBLE IN DERIVATIVES":
            charts_html = "\n".join(build_chart_grid_for_record(r) for r in recs)
        else:
            charts_html = ""

        per_key_sections.append(f"""
        <section class="key-section">
            <h3>Category: {html.escape(str(key_name))} (Total: {len(recs)})</h3>
            <div class="key-table">{table_html}</div>
            {charts_html}
        </section>
        """)

    # ----------- CSS -----------
    css = """
    <style>
    body { font-family: Arial; padding: 16px; background: #fff; color: #111; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 14px; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; font-size: 13px; }
    th { background: #007bff; color: white; position: sticky; top: 0; }

    .scroll { max-height: 420px; overflow: auto; padding: 6px; background: #fafafa;
              margin-bottom: 16px; border: 1px solid #ddd; }

    .key-section {
        border: 1px solid #e6eef6;
        background: #fbfeff;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 30px;
    }

    .chart-flex-block {
        border: 1px solid #ddd;
        background: #fff;
        padding: 8px;
        border-radius: 6px;
        margin-bottom: 14px;
    }

    .chart-title { margin-bottom: 6px; font-size: 14px; }

    .chart-flex-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .chart-flex-item {
        flex: 1 1 300px;
        min-height: 180px;
        border: 1px solid #ccc;
        border-radius: 6px;
        overflow: hidden;
    }

    .chart-flex-item iframe {
        width: 100%;
        height: 100%;
        border: 0;
    }
    </style>
    """

    # ----------- FINAL HTML -----------
    html_out = "\n".join([
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>NSE Indices</title>",
        css,
        "</head><body>",
        "<h1>NSE Indices — Full Static Render</h1>",
        f"<div class='meta'>Generated: {html.escape(dt.now().strftime('%Y-%m-%d %H:%M:%S'))}</div>",
        "<h2>Main Indices Table</h2>",
        "<div class='scroll'>", main_table_html, "</div>",
        "<h2>Dates / Meta</h2>" if dates_table_html else "",
        "<div class='scroll'>" if dates_table_html else "",
        dates_table_html,
        "</div>" if dates_table_html else "",
        "<h2>Categories</h2>",
        *per_key_sections,
        "</body></html>"
    ])

    # ================= SAVE CACHE =================
    save(cache_key, {
        "date": today,
        "html": html_out
    })

    return html_out
