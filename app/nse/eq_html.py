from app.nse import nsepythonmodified as ns
import pandas as pd
from datetime import datetime
import re


def build_eq_html(symbol):
    """
    Build full HTML page for eq(symbol) output with professional card-based display
    Returns: HTML string
    """

    # -------------------------------------------------------
    # CALL eq() function
    # -------------------------------------------------------
    try:
        out = ns.eq(symbol)
        print(out)
    except Exception as e:
        return f"<h3>Error: Failed to fetch data for {symbol}</h3>"

    if not isinstance(out, dict):
        return "<h3>Error: EQ data not available</h3>"

    # -------------------------------------------------------
    # Helper: Format key names
    # -------------------------------------------------------
    def format_key(key):
        """Convert camelCase/snake_case to readable title"""
        try:
            formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', str(key))
            return formatted.replace('_', ' ').title()
        except:
            return str(key)

    # -------------------------------------------------------
    # Helper: Format values
    # -------------------------------------------------------
    def format_value(value):
        """Format value with appropriate styling"""
        if isinstance(value, pd.DataFrame):
            if value.empty:
                return '<span class="badge">Empty</span>'
            return f'<span class="badge info">{len(value)} rows</span>'
        
        if isinstance(value, pd.Series):
            if len(value) == 1:
                return format_value(value.iloc[0])
            return f'<span class="badge info">{len(value)} items</span>'
        
        if value is None or (isinstance(value, str) and value == ""):
            return '<span class="badge">N/A</span>'
        
        if isinstance(value, bool):
            status = "success" if value else "danger"
            text = "Yes" if value else "No"
            return f'<span class="badge {status}">{text}</span>'
        
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                return f"{value:,.2f}"
            return f"{value:,}"
        
        if isinstance(value, str):
            lower = value.lower()
            if lower in ["active", "open", "yes", "true", "up"]:
                return f'<span class="badge success">{value}</span>'
            elif lower in ["inactive", "closed", "no", "false", "down", "suspended"]:
                return f'<span class="badge danger">{value}</span>'
            elif lower in ["pending", "hold", "partial"]:
                return f'<span class="badge warning">{value}</span>'
            return value
        
        if isinstance(value, (list, dict)):
            return f'<span class="badge info">{len(value)} items</span>'
        
        return str(value)

    # -------------------------------------------------------
    # Helper: Convert DataFrame to cards
    # -------------------------------------------------------
    def df_to_cards(df, priority_cols=None):
        """Convert DataFrame to card grid"""
        if df is None or df.empty:
            return '<div class="empty">No data available</div>'
        
        if not isinstance(df, pd.DataFrame):
            return f'<div class="card"><div class="card-value">{format_value(df)}</div></div>'
        
        priority_cols = priority_cols or []
        cards_html = '<div class="cards-grid">'
        
        # Single row DataFrame - cards for each column
        if len(df) == 1:
            row = df.iloc[0]
            processed = set()
            
            # Priority columns first
            for col in priority_cols:
                if col in df.columns:
                    val = row[col]
                    cards_html += f'''
                    <div class="card highlight">
                        <div class="card-label">{format_key(col)}</div>
                        <div class="card-value">{format_value(val)}</div>
                    </div>'''
                    processed.add(col)
            
            # Remaining columns
            for col in df.columns:
                if col not in processed:
                    val = row[col]
                    cards_html += f'''
                    <div class="card">
                        <div class="card-label">{format_key(col)}</div>
                        <div class="card-value">{format_value(val)}</div>
                    </div>'''
        else:
            # Multi-row - show as table
            return df_to_list_table(df)
        
        cards_html += '</div>'
        return cards_html

    # -------------------------------------------------------
    # Helper: Multi-row DataFrame to list table
    # -------------------------------------------------------
    def df_to_list_table(df):
        """Convert DataFrame to responsive list view"""
        if df is None or df.empty:
            return '<div class="empty">No data available</div>'
        
        cols = df.columns.tolist()
        
        html = '<div class="list-container">'
        html += '<div class="list-header">'
        for col in cols:
            html += f'<div>{format_key(col)}</div>'
        html += '</div>'
        
        for idx, row in df.iterrows():
            html += '<div class="list-row">'
            for col in cols:
                val = row[col]
                html += f'<div class="list-cell">{format_value(val)}</div>'
            html += '</div>'
        
        html += '</div>'
        return html

    # -------------------------------------------------------
    # Helper: Route data to appropriate converter
    # -------------------------------------------------------
    def data_to_cards(data, priority=None):
        """Route data to appropriate converter based on type"""
        if isinstance(data, pd.DataFrame):
            return df_to_cards(data, priority)
        elif isinstance(data, pd.Series):
            return df_to_cards(data.to_frame().T, priority)
        elif isinstance(data, list):
            if len(data) == 0:
                return '<div class="empty">No data available</div>'
            if isinstance(data[0], dict):
                return df_to_list_table(pd.DataFrame(data))
            return f'<div class="card"><div class="card-value">{", ".join(str(x) for x in data)}</div></div>'
        elif isinstance(data, dict):
            return df_to_cards(pd.DataFrame([data]), priority)
        else:
            return f'<div class="card"><div class="card-value">{format_value(data)}</div></div>'

    # -------------------------------------------------------
    # SECTION CONFIGURATION
    # -------------------------------------------------------
    sections_config = {
        "metadata": {"title": "Company Overview", "icon": "🏢", "priority": ["symbol", "companyName", "industry", "sector"]},
        "securityInfo": {"title": "Security Information", "icon": "🔒", "priority": ["boardStatus", "tradingStatus", "classOfShare", "faceValue"]},
        "priceInfo": {"title": "Price Information", "icon": "💰", "priority": ["lastPrice", "change", "pChange", "open", "high", "low", "previousClose"]},
        "industryInfo": {"title": "Industry Classification", "icon": "🏭", "priority": ["macro", "sector", "industry", "basicIndustry"]},
        "pdSectorIndAll": {"title": "Index Participation", "icon": "📊"},
        "info": {"title": "Trading Details", "icon": "ℹ️", "priority": ["symbol", "isFNOSec", "isSLBSec", "isETFSec"]},
        "preOpen": {"title": "Pre-Open Market", "icon": "🌅"},
        "preOpenMarket": {"title": "Pre-Open Summary", "icon": "📈", "priority": ["IEP", "totalTradedVolume"]}
    }

    section_order = list(sections_config.keys())

    # -------------------------------------------------------
    # BUILD SECTIONS
    # -------------------------------------------------------
    sections_html = ""
    for sec in section_order:
        config = sections_config.get(sec, {})
        title = config.get("title", format_key(sec))
        icon = config.get("icon", "📋")
        priority = config.get("priority", [])
        
        val = out.get(sec)
        
        # Skip if no data
        if val is None:
            continue
        if isinstance(val, pd.DataFrame) and val.empty:
            continue
        if isinstance(val, list) and len(val) == 0:
            continue
        if isinstance(val, dict) and len(val) == 0:
            continue
        
        # Build content
        content = data_to_cards(val, priority)
        
        sections_html += f'''
        <div class="section">
            <div class="section-header">
                <div class="section-title"><span class="icon">{icon}</span> {title}</div>
            </div>
            <div class="section-body">
                {content}
            </div>
        </div>'''

    # -------------------------------------------------------
    # FINAL HTML
    # -------------------------------------------------------
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Equity Report - {symbol}</title>
<style>
:root {{
    --primary: #1a5f9e;
    --primary-light: #2980b9;
    --accent: #e74c3c;
    --success: #27ae60;
    --warning: #f39c12;
    --bg: #f0f2f5;
    --card-bg: #ffffff;
    --border: #e1e8ed;
    --text: #2c3e50;
    --text-muted: #7f8c8d;
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
    --shadow-hover: 0 4px 16px rgba(0,0,0,0.12);
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}}

.header {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: white;
    padding: 30px 20px;
    text-align: center;
    box-shadow: var(--shadow);
}}

.header h1 {{
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 8px;
}}

.header .subtitle {{
    opacity: 0.9;
    font-size: 16px;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

.section {{
    background: var(--card-bg);
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: var(--shadow);
    overflow: hidden;
    animation: fadeIn 0.5s ease-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.section-header {{
    padding: 16px 20px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-bottom: 1px solid var(--border);
}}

.section-title {{
    font-size: 18px;
    font-weight: 700;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-title .icon {{
    font-size: 22px;
}}

.section-body {{
    padding: 20px;
}}

/* Cards Grid */
.cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
}}

.card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.card:hover {{
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
    border-color: var(--primary-light);
}}

.card.highlight {{
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border: 2px solid var(--primary-light);
    border-left: 4px solid var(--primary);
}}

.card-label {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 6px;
    font-weight: 600;
}}

.card-value {{
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
    word-break: break-word;
}}

/* List Container */
.list-container {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
}}

.list-header {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    padding: 14px 16px;
    background: var(--primary);
    color: white;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.list-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    background: white;
    transition: background 0.2s;
}}

.list-row:hover {{
    background: #f8f9fa;
}}

.list-row:last-child {{
    border-bottom: none;
}}

.list-cell {{
    font-size: 14px;
    color: var(--text);
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}}

.badge.success {{
    background: #d4edda;
    color: #155724;
}}

.badge.danger {{
    background: #f8d7da;
    color: #721c24;
}}

.badge.warning {{
    background: #fff3cd;
    color: #856404;
}}

.badge.info {{
    background: #d1ecf1;
    color: #0c5460;
}}

.empty {{
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
    font-style: italic;
}}

/* Responsive */
@media (max-width: 768px) {{
    .header h1 {{
        font-size: 28px;
    }}
    
    .cards-grid {{
        grid-template-columns: 1fr;
    }}
    
    .list-header,
    .list-row {{
        grid-template-columns: 1fr;
        gap: 8px;
    }}
    
    .list-header {{
        display: none;
    }}
    
    .list-row {{
        padding: 16px;
        border: 1px solid var(--border);
        border-radius: 8px;
        margin-bottom: 8px;
    }}
}}
</style>
</head>
<body>
<div class="header">
    <h1>{symbol.upper()}</h1>
    <div class="subtitle">Equity Report • {datetime.now().strftime("%B %d, %Y")}</div>
</div>

<div class="container">
    {sections_html}
</div>
</body>
</html>'''

    return html
    