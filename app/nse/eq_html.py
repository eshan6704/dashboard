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
        print(f"DEBUG - API Response for {symbol}:", out)
    except Exception as e:
        print(f"DEBUG - Error calling ns.eq({symbol}):", str(e))
        return f"<h3>Error: Failed to fetch data for {symbol}</h3>"

    if not isinstance(out, dict):
        print(f"DEBUG - Invalid response type:", type(out))
        return "<h3>Error: EQ data not available</h3>"

    # -------------------------------------------------------
    # Helper: Format key names
    # -------------------------------------------------------
    def format_key(key):
        """Convert camelCase/snake_case to readable title"""
        try:
            # Insert space before capital letters
            formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', str(key))
            return formatted.replace('_', ' ').title()
        except:
            return str(key)

    # -------------------------------------------------------
    # Helper: Format values with badges
    # -------------------------------------------------------
    def format_value(value):
        """Format value with appropriate styling"""
        if value is None or value == "":
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
    # Helper: Build cards from dict
    # -------------------------------------------------------
    def dict_to_cards(data, priority_keys=None):
        """Convert dictionary to card grid HTML"""
        if not data or not isinstance(data, dict):
            return '<div class="empty">No data available</div>'
        
        priority_keys = priority_keys or []
        cards_html = '<div class="cards-grid">'
        
        # Priority items first
        processed = set()
        for key in priority_keys:
            if key in data:
                val = data[key]
                cards_html += f'''
                <div class="card highlight">
                    <div class="card-label">{format_key(key)}</div>
                    <div class="card-value">{format_value(val)}</div>
                </div>'''
                processed.add(key)
        
        # Remaining items
        for key, val in data.items():
            if key not in processed:
                cards_html += f'''
                <div class="card">
                    <div class="card-label">{format_key(key)}</div>
                    <div class="card-value">{format_value(val)}</div>
                </div>'''
        
        cards_html += '</div>'
        return cards_html

    # -------------------------------------------------------
    # Helper: Build list table
    # -------------------------------------------------------
    def list_to_cards(data):
        """Convert list of dicts to responsive list view"""
        if not data or not isinstance(data, list) or len(data) == 0:
            return '<div class="empty">No data available</div>'
        
        # If simple list
        if not isinstance(data[0], dict):
            items = ", ".join(str(x) for x in data)
            return f'<div class="card"><div class="card-value">{items}</div></div>'
        
        # List of dicts - create header row
        keys = list(data[0].keys())
        
        html = '<div class="list-container">'
        html += '<div class="list-header">'
        for key in keys:
            html += f'<div>{format_key(key)}</div>'
        html += '</div>'
        
        for item in data:
            html += '<div class="list-row">'
            for key in keys:
                val = item.get(key, "")
                html += f'<div class="list-cell">{format_value(val)}</div>'
            html += '</div>'
        
        html += '</div>'
        return html

    # -------------------------------------------------------
    # SECTION CONFIGURATION
    # -------------------------------------------------------
    sections_config = {
        "metadata": {"title": "Company Overview", "icon": "🏢", "priority": ["symbol", "companyName", "industry", "sector"]},
        "securityInfo": {"title": "Security Information", "icon": "🔒", "priority": ["boardStatus", "tradingStatus", "classOfShare", "faceValue"]},
        "priceInfo": {"title": "Price Information", "icon": "💰", "priority": ["lastPrice", "change", "pChange", "open", "high", "low", "previousClose"]},
        "industryInfo": {"title": "Industry Classification", "icon": "🏭", "priority": ["macro", "sector", "industry", "basicIndustry"]},
        "pdSectorIndAll": {"title": "Index Participation", "icon": "📊", "type": "list"},
        "info": {"title": "Trading Details", "icon": "ℹ️", "priority": ["symbol", "isFNOSec", "isSLBSec", "isETFSec"]},
        "preOpen": {"title": "Pre-Open Market", "icon": "🌅", "type": "list"},
        "preOpenMarket": {"title": "Pre-Open Summary", "icon": "📈", "type": "dict"}
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
        sec_type = config.get("type", "dict")
        priority = config.get("priority", [])
        
        val = out.get(sec)
        
        # Skip if no data
        if val is None or (isinstance(val, (dict, list)) and len(val) == 0):
            continue
        
        # Build content based on type
        if sec_type == "list" and isinstance(val, list):
            content = list_to_cards(val)
        elif isinstance(val, dict):
            content = dict_to_cards(val, priority)
        elif isinstance(val, list):
            content = list_to_cards(val)
        else:
            content = f'<div class="card"><div class="card-value">{format_value(val)}</div></div>'
        
        sections_html += f'''
        <div class="section">
            <div class="section-header" onclick="toggleSection('{sec}')">
                <div class="section-title"><span class="icon">{icon}</span> {title}</div>
                <button class="toggle-btn">View / Hide</button>
            </div>
            <div id="{sec}" class="section-body">
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
}}

.section-header:hover {{
    background: #f0f3f6;
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

.toggle-btn {{
    background: var(--primary);
    color: white;
    border: none;
    padding: 6px 12px;
    font-size: 12px;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
}}

.section-body {{
    padding: 20px;
    display: none;
}}

.section-body.active {{
    display: block;
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

<script>
function toggleSection(id) {{
    let body = document.getElementById(id);
    if (body.style.display === "none" || body.style.display === "") {{
        body.style.display = "block";
    }} else {{
        body.style.display = "none";
    }}
}}
// Open first section by default
document.addEventListener('DOMContentLoaded', function() {{
    let firstSection = document.querySelector('.section-body');
    if (firstSection) firstSection.style.display = 'block';
}});
</script>
</body>
</html>'''

    return html
    