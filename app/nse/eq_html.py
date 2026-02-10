from app.nse import nsepythonmodified as ns
import pandas as pd
from datetime import datetime
import re


def build_eq_html(symbol):
    """
    Build full HTML page for eq(symbol) output - displays ALL data dynamically
    Returns: HTML string
    """

    # -------------------------------------------------------
    # CALL eq() function
    # -------------------------------------------------------
    try:
        out = ns.eq(symbol)
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
    def format_value(value, key=None):
        """Format value with appropriate styling"""
        # Handle pandas objects
        if isinstance(value, pd.DataFrame):
            if value.empty:
                return '<span class="badge">Empty</span>'
            return f'<span class="badge info">{len(value)} rows × {len(value.columns)} cols</span>'
        
        if isinstance(value, pd.Series):
            if len(value) == 1:
                return format_value(value.iloc[0], key)
            return f'<span class="badge info">Series ({len(value)} items)</span>'
        
        # Handle None/empty
        if value is None:
            return '<span class="badge">N/A</span>'
        
        if isinstance(value, str) and value == "":
            return '<span class="badge">N/A</span>'
        
        # Handle booleans
        if isinstance(value, bool):
            status = "success" if value else "danger"
            text = "Yes" if value else "No"
            return f'<span class="badge {status}">{text}</span>'
        
        # Handle numbers - check for change fields
        if isinstance(value, (int, float)):
            # Check if this is a change field for color coding
            if key and any(x in key.lower() for x in ['change', 'pchange', 'variation', 'percent']):
                if isinstance(value, (int, float)) and value < 0:
                    return f'<span style="color: #e74c3c; font-weight: 700;">{value:,.2f}</span>'
                elif isinstance(value, (int, float)) and value > 0:
                    return f'<span style="color: #27ae60; font-weight: 700;">+{value:,.2f}</span>'
            if isinstance(value, float):
                return f"{value:,.2f}"
            return f"{value:,}"
        
        # Handle strings with status keywords
        if isinstance(value, str):
            lower = value.lower()
            if lower in ["active", "open", "yes", "true", "up", "main"]:
                return f'<span class="badge success">{value}</span>'
            elif lower in ["inactive", "closed", "no", "false", "down", "suspended", "delisted"]:
                return f'<span class="badge danger">{value}</span>'
            elif lower in ["pending", "hold", "partial"]:
                return f'<span class="badge warning">{value}</span>'
            return value
        
        # Handle lists/dicts
        if isinstance(value, (list, dict)):
            return f'<span class="badge info">{len(value)} items</span>'
        
        return str(value)

    # -------------------------------------------------------
    # Helper: Convert any data to cards
    # -------------------------------------------------------
    def data_to_cards(data, section_name=""):
        """Convert any data type to HTML display"""
        
        # DataFrame handling
        if isinstance(data, pd.DataFrame):
            if data.empty:
                return '<div class="empty">No data available</div>'
            
            # Single row - cards for each column
            if len(data) == 1:
                cards_html = '<div class="cards-grid">'
                row = data.iloc[0]
                
                for col in data.columns:
                    val = row[col]
                    # Highlight important fields
                    is_important = any(x in col.lower() for x in 
                        ['price', 'change', 'name', 'symbol', 'status', 'last', 'close', 'open', 'high', 'low'])
                    
                    card_class = "card highlight" if is_important else "card"
                    cards_html += f'''
                    <div class="{card_class}">
                        <div class="card-label">{format_key(col)}</div>
                        <div class="card-value">{format_value(val, col)}</div>
                    </div>'''
                
                cards_html += '</div>'
                return cards_html
            
            # Multi-row - table view
            else:
                return df_to_table(data)
        
        # Series handling
        elif isinstance(data, pd.Series):
            return data_to_cards(data.to_frame().T, section_name)
        
        # List handling
        elif isinstance(data, list):
            if len(data) == 0:
                return '<div class="empty">No data available</div>'
            
            # List of dicts - convert to DataFrame
            if isinstance(data[0], dict):
                return df_to_table(pd.DataFrame(data))
            
            # Simple list
            items_html = "".join([f'<div class="card"><div class="card-value">{format_value(x)}</div></div>' for x in data])
            return f'<div class="cards-grid">{items_html}</div>'
        
        # Dict handling
        elif isinstance(data, dict):
            cards_html = '<div class="cards-grid">'
            for key, val in data.items():
                cards_html += f'''
                <div class="card">
                    <div class="card-label">{format_key(key)}</div>
                    <div class="card-value">{format_value(val, key)}</div>
                </div>'''
            cards_html += '</div>'
            return cards_html
        
        # Single value
        else:
            return f'<div class="card"><div class="card-value">{format_value(data)}</div></div>'

    # -------------------------------------------------------
    # Helper: DataFrame to table (for multi-row)
    # -------------------------------------------------------
    def df_to_table(df):
        """Convert DataFrame to HTML table"""
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
                html += f'<div class="list-cell">{format_value(val, col)}</div>'
            html += '</div>'
        
        html += '</div>'
        return html

    # -------------------------------------------------------
    # Build ALL sections dynamically from API response
    # -------------------------------------------------------
    sections_html = ""
    
    # Process ALL keys in the API response (not just hardcoded ones)
    for section_key in out.keys():
        data = out[section_key]
        
        # Skip None or empty
        if data is None:
            continue
        if isinstance(data, pd.DataFrame) and data.empty:
            continue
        if isinstance(data, list) and len(data) == 0:
            continue
        if isinstance(data, dict) and len(data) == 0:
            continue
        
        # Format section title
        title = format_key(section_key)
        
        # Generate icon based on section name
        icon = "📋"
        lower_key = section_key.lower()
        if any(x in lower_key for x in ['price', 'value', 'cost']):
            icon = "💰"
        elif any(x in lower_key for x in ['sec', 'board', 'status']):
            icon = "🔒"
        elif any(x in lower_key for x in ['company', 'meta', 'info']):
            icon = "🏢"
        elif any(x in lower_key for x in ['industry', 'sector']):
            icon = "🏭"
        elif any(x in lower_key for x in ['index', 'nifty', 'sensex']):
            icon = "📊"
        elif any(x in lower_key for x in ['preopen', 'market', 'trade']):
            icon = "📈"
        elif any(x in lower_key for x in ['week', 'day', 'high', 'low']):
            icon = "📅"
        
        # Build content
        content = data_to_cards(data, section_key)
        
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
    max-width: 1400px;
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
    border-bottom: 2px solid var(--primary);
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
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
    <div class="subtitle">Complete Equity Report • {datetime.now().strftime("%B %d, %Y at %H:%M")}</div>
</div>

<div class="container">
    {sections_html}
</div>
</body>
</html>'''

    return html
    