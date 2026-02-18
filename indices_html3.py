import pandas as pd
from app.nse import nsepythonmodified as ns
import html
from datetime import datetime as dt

# Your allowed indices list
ALLOWED_INDICES = [
    "NIFTY 50", "NIFTY 100", "NIFTY 200", "NIFTY 500", "NIFTY BANK",
    "NIFTY FIN SERVICE", "INDIA VIX", "NIFTY MIDCAP 150", "NIFTY SMLCAP 250",
    "NIFTY MIDSML 400", "NIFTY TOTAL MKT", "NIFTY MICROCAP250", "NIFTY AUTO",
    "NIFTY FMCG", "NIFTY IT", "NIFTY MEDIA", "NIFTY METAL", "NIFTY PHARMA",
    "NIFTY PSU BANK", "NIFTY PVT BANK", "NIFTY REALTY", "NIFTY HEALTHCARE",
    "NIFTY CONSR DURBL", "NIFTY OIL AND GAS", "NIFTY CHEMICALS", "NIFTY COMMODITIES",
    "NIFTY CONSUMPTION", "NIFTY CPSE", "NIFTY ENERGY", "NIFTY INFRA", "NIFTY MNC",
    "NIFTY PSE", "NIFTY SERV SECTOR", "NIFTY IND DIGITAL", "NIFTY IND DEFENCE",
    "NIFTY IND TOURISM", "NIFTY CAPITAL MKT", "NIFTY EV"
]


def build_indices_html():
    """
    Generates simplified HTML for NSE Indices
    - Only allowed indices
    - Only indexSymbol column + data columns (no key, no index)
    - Dates table on top
    - No category sections
    """

    # Fetch data
    p = ns.indices()
    data_df = p.get("data", pd.DataFrame())
    dates_df = p.get("dates", pd.DataFrame())

    if data_df.empty:
        return "<p>No data available.</p>"

    # Filter to allowed indices only
    records = data_df.to_dict(orient="records")
    filtered_records = [
        r for r in records 
        if r.get("indexSymbol") in ALLOWED_INDICES
    ]

    if not filtered_records:
        return "<p>No matching indices found.</p>"

    # Columns to exclude (key, index, and hidden metadata)
    exclude_cols = {
        "key", "index", "chartTodayPath", "chart30dPath", "chart30Path", 
        "chart365dPath", "date365dAgo", "date30dAgo", "previousDay", 
        "oneWeekAgo", "oneMonthAgoVal", "oneWeekAgoVal", "oneYearAgoVal",
        "indicativeClose"
    }

    # Get all columns from first record, excluding unwanted
    all_cols = list(filtered_records[0].keys())
    display_cols = [c for c in all_cols if c not in exclude_cols]

    # Reorder: indexSymbol first, then others
    if "indexSymbol" in display_cols:
        display_cols.remove("indexSymbol")
        display_cols = ["indexSymbol"] + display_cols

    # ================= TABLE BUILDER =================
    def build_table(recs, cols):
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

    # Build dates table
    dates_html = ""
    if not dates_df.empty:
        dates_records = dates_df.to_dict(orient="records")
        # Get columns excluding internal ones
        dates_cols = [c for c in dates_records[0].keys() if c not in exclude_cols and not c.startswith("_")]
        dates_html = build_table(dates_records, dates_cols)

    # Build main indices table
    main_html = build_table(filtered_records, display_cols)

    # ================= CSS =================
    css = """
    <style>
    body { 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
        padding: 20px; 
        background: #f8fafc; 
        color: #1e293b; 
        margin: 0;
    }
    h2 { 
        color: #334155; 
        font-size: 18px; 
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    table { 
        border-collapse: collapse; 
        width: 100%; 
        margin-bottom: 16px;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-radius: 8px;
        overflow: hidden;
    }
    th, td { 
        border: 1px solid #e2e8f0; 
        padding: 10px 12px; 
        font-size: 13px;
        text-align: left;
    }
    th { 
        background: #3b82f6; 
        color: #fff; 
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    tr:nth-child(even) { background: #f8fafc; }
    tr:hover { background: #eff6ff; }
    td { color: #475569; }
    
    /* First column (indexSymbol) styling */
    td:first-child, th:first-child {
        font-weight: 600;
        color: #1e40af;
        background: #eff6ff;
    }
    
    .scroll { 
        max-height: 600px; 
        overflow: auto;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .dates-section {
        background: white;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .dates-section h2 {
        margin-top: 0;
        color: #059669;
        border-bottom-color: #10b981;
    }
    .main-section {
        background: white;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .count-badge {
        display: inline-block;
        background: #3b82f6;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    </style>
    """

    # ================= FINAL HTML =================
    count_badge = f'<span class="count-badge">{len(filtered_records)} indices</span>'
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>NSE Indices</title>",
        css,
        "</head>",
        "<body>",
        
        # Dates section on top
        '<div class="dates-section">' if dates_html else "",
        '<h2>📅 Market Dates</h2>' if dates_html else "",
        '<div class="scroll">' if dates_html else "",
        dates_html if dates_html else "",
        '</div>' if dates_html else "",
        '</div>' if dates_html else "",
        
        # Main indices table
        '<div class="main-section">',
        f'<h2>📊 Indices {count_badge}</h2>',
        '<div class="scroll">',
        main_html,
        '</div>',
        '</div>',
        
        "</body></html>"
    ]

    return "".join(html_parts)