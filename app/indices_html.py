import pandas as pd
from . import nsepythonmodified as ns
import html
from datetime import datetime as dt
from collections import defaultdict

# persist helpers (HF only)
from .persist import exists, load, save


def build_indices_html():
    """
    Generates full static HTML for NSE Indices
    - Tables for all indices
    - Category-wise tables
    - Charts ONLY for 'INDICES ELIGIBLE IN DERIVATIVES'
    - DAILY cache via persist.py (HTML only)
    """

    # ================= CACHE (TTL handled by persist) =================
    cache_name = "DAILY_INDICES_HTML"

    if exists(cache_name, "html"):
        cached_html = load(cache_name, "html")
        if isinstance(cached_html, str):
            return cached_html

    # ================= FETCH DATA =================
    p = ns.indices()
    data_df = p.get("data", pd.DataFrame())
    dates_df = p.get("dates", pd.DataFrame())

    records = data_df.to_dict(orient="records") if not data_df.empty else []

    hidden_cols = {
        "key", "chartTodayPath", "chart30dPath", "chart30Path", "chart365dPath",
        "date365dAgo", "date30dAgo", "previousDay", "oneWeekAgo",
        "oneMonthAgoVal", "oneWeekAgoVal", "oneYearAgoVal",
        "index", "indicativeClose"
    }

    # ================= TABLE BUILDER =================
    def build_table(recs, cols=None):
        if not recs:
            return "<p>No data available.</p>"

        if cols is None:
            cols = []
            for r in recs:
                for k in r:
                    if k not in cols:
                        cols.append(k)

        header = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols)

        body = []
        for r in recs:
            tds = []
            for c in cols:
                v = r.get(c, "")
                if isinstance(v, (dict, list)):
                    v = str(v)
                tds.append(f"<td>{html.escape(str(v) if v is not None else '')}</td>")
            body.append("<tr>" + "".join(tds) + "</tr>")

        return f"""
        <table>
            <thead><tr>{header}</tr></thead>
            <tbody>{''.join(body)}</tbody>
        </table>
        """

    # ================= CHART BUILDER =================
    def build_chart_block(r):
        def iframe(src, label):
            if src and isinstance(src, str):
                return f"""
                <div class="chart-flex-item">
                    <iframe src="{html.escape(src)}" loading="lazy"
                            frameborder="0" title="{html.escape(label)}"></iframe>
                </div>
                """
            return ""

        charts = (
            iframe(r.get("chartTodayPath"), "Today") +
            iframe(r.get("chart30dPath"), "30 Days") +
            iframe(r.get("chart365dPath"), "1 Year")
        )

        if not charts.strip():
            return ""

        title = r.get("indexSymbol") or r.get("index") or r.get("symbol") or ""

        return f"""
        <div class="chart-flex-block">
            <div class="chart-title"><strong>{html.escape(title)}</strong></div>
            <div class="chart-flex-container">{charts}</div>
        </div>
        """

    # ================= MAIN TABLE =================
    main_table_html = build_table(records)

    # ================= DATES TABLE =================
    dates_table_html = ""
    if not dates_df.empty:
        dates_table_html = build_table(
            dates_df.to_dict(orient="records")
        )

    # ================= GROUP BY CATEGORY =================
    groups = defaultdict(list)
    for r in records:
        groups[r.get("key") or "UNCLASSIFIED"].append(r)

    sections = []

    for key_name, recs in groups.items():
        first = recs[0]
        cols = [c for c in first if c not in hidden_cols]

        preferred = ["indexSymbol", "index", "symbol", "name"]
        ordered_cols = (
            [c for c in preferred if c in cols] +
            [c for c in cols if c not in preferred]
        )

        table_html = build_table(recs, ordered_cols)

        charts_html = ""
        if str(key_name).strip().upper() == "INDICES ELIGIBLE IN DERIVATIVES":
            charts_html = "\n".join(build_chart_block(r) for r in recs)

        sections.append(f"""
        <section class="key-section">
            <h3>{html.escape(str(key_name))} (Total: {len(recs)})</h3>
            {table_html}
            {charts_html}
        </section>
        """)

    # ================= CSS =================
    css = """
    <style>
    body { font-family: Arial; padding: 16px; background: #fff; color: #111; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 12px; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; font-size: 13px; }
    th { background: #007bff; color: #fff; position: sticky; top: 0; }

    .scroll { max-height: 420px; overflow: auto; margin-bottom: 20px; }

    .key-section {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 30px;
        background: #fafcff;
    }

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

    .chart-title {
        font-size: 14px;
        margin-bottom: 6px;
    }
    </style>
    """

    # ================= FINAL HTML =================
    html_out = "\n".join([
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>NSE Indices</title>",
        css,
        "</head>",
        "<body>",
        "<h1>NSE Indices</h1>",
        f"<div>Generated: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
        "<h2>Main Indices</h2>",
        "<div class='scroll'>", main_table_html, "</div>",
        "<h2>Dates</h2>" if dates_table_html else "",
        "<div class='scroll'>" if dates_table_html else "",
        dates_table_html,
        "</div>" if dates_table_html else "",
        "<h2>Categories</h2>",
        *sections,
        "</body></html>"
    ])

    # ================= SAVE HTML (HF only) =================
    save(cache_name, html_out, "html")

    return html_out