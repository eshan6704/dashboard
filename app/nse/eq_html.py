from app.nse import nsepythonmodified as ns
import pandas as pd
from typing import Dict, Any, Optional, Union
from datetime import datetime
import re


class EquityReportBuilder:
    """Professional HTML report generator for NSE equity data with card-based layout."""
    
    # Define how to organize and display each section
    SECTION_CONFIG = {
        "metadata": {
            "title": "Company Overview",
            "icon": "🏢",
            "priority": ["symbol", "companyName", "industry", "sector", "listingDate"]
        },
        "securityInfo": {
            "title": "Security Information", 
            "icon": "🔒",
            "priority": ["boardStatus", "tradingStatus", "classOfShare", "faceValue", "issuedSize"]
        },
        "priceInfo": {
            "title": "Price Information",
            "icon": "💰",
            "priority": ["lastPrice", "change", "pChange", "open", "high", "low", "previousClose", "vwap"]
        },
        "industryInfo": {
            "title": "Industry Classification",
            "icon": "🏭",
            "priority": ["macro", "sector", "industry", "basicIndustry"]
        },
        "pdSectorIndAll": {
            "title": "Index Participation",
            "icon": "📊",
            "type": "list"
        },
        "info": {
            "title": "Trading Details",
            "icon": "ℹ️",
            "priority": ["symbol", "isFNOSec", "isSLBSec", "isETFSec", "isDelisted"]
        },
        "preOpen": {
            "title": "Pre-Open Market",
            "icon": "🌅",
            "type": "list"
        },
        "preOpenMarket": {
            "title": "Pre-Open Summary",
            "icon": "📈",
            "priority": ["IEP", "totalTradedVolume"]
        }
    }
    
    SECTION_ORDER = list(SECTION_CONFIG.keys())
    
    HTML_TEMPLATE = """<!DOCTYPE html>
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
            padding: 0;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }}
        
        .symbol-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            margin-bottom: 12px;
            backdrop-filter: blur(10px);
        }}
        
        h1 {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            opacity: 0.9;
            font-size: 16px;
            font-weight: 400;
        }}
        
        .timestamp {{
            margin-top: 16px;
            font-size: 13px;
            opacity: 0.8;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        
        .section {{
            margin-bottom: 30px;
            animation: fadeIn 0.5s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }}
        
        .section-icon {{
            font-size: 24px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--card-bg);
            border-radius: 10px;
            box-shadow: var(--shadow);
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: var(--primary);
            flex: 1;
        }}
        
        .section-toggle {{
            background: none;
            border: none;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        
        .section-toggle:hover {{
            background: var(--bg);
        }}
        
        .chevron {{
            width: 20px;
            height: 20px;
            transition: transform 0.3s;
            color: var(--text-muted);
        }}
        
        .section.collapsed .chevron {{
            transform: rotate(-90deg);
        }}
        
        .section-body {{
            display: grid;
            gap: 16px;
        }}
        
        .section.collapsed .section-body {{
            display: none;
        }}
        
        /* Card Grid Layout */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .card:hover {{
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .card:hover::before {{
            opacity: 1;
        }}
        
        .card-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 6px;
            font-weight: 600;
        }}
        
        .card-value {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text);
            word-break: break-word;
        }}
        
        .card-value.number {{
            font-family: 'SF Mono', Monaco, monospace;
            color: var(--primary);
        }}
        
        .card-value.positive {{
            color: var(--success);
        }}
        
        .card-value.negative {{
            color: var(--accent);
        }}
        
        /* Special Cards */
        .card.highlight {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border: 2px solid var(--primary-light);
        }}
        
        .card.highlight .card-value {{
            font-size: 24px;
            color: var(--primary);
        }}
        
        /* List/Table Cards for complex data */
        .list-card {{
            grid-column: 1 / -1;
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }}
        
        .list-header {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            padding: 16px 20px;
            background: var(--primary);
            color: white;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .list-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
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
        
        .list-cell.muted {{
            color: var(--text-muted);
        }}
        
        /* Status badges */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge.danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge.info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
        }}
        
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
        
        /* Error State */
        .error-container {{
            max-width: 600px;
            margin: 100px auto;
            text-align: center;
            padding: 40px;
        }}
        
        .error-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        
        .error-message {{
            background: #fee;
            color: #c33;
            padding: 16px 24px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #c33;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            h1 {{
                font-size: 32px;
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
        
        /* Print styles */
        @media print {{
            .section-toggle {{
                display: none;
            }}
            .section-body {{
                display: block !important;
            }}
            .card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {header}
    <div class="container">
        {content}
    </div>
    
    <script>
        document.querySelectorAll('.section-toggle').forEach(btn => {{
            btn.addEventListener('click', () => {{
                btn.closest('.section').classList.toggle('collapsed');
            }});
        }});
    </script>
</body>
</html>"""
    
    @classmethod
    def build(cls, symbol: str) -> str:
        """Generate professional HTML equity report."""
        try:
            data = ns.eq(symbol)
        except Exception as e:
            return cls._build_error_html(symbol, str(e))
        
        if not isinstance(data, dict):
            return cls._build_error_html(symbol, "Invalid data format")
        
        # Build header
        company_name = cls._extract_company_name(data)
        header_html = cls._build_header(symbol, company_name)
        
        # Build sections - handle missing keys gracefully
        sections_html = ""
        for section_key in cls.SECTION_ORDER:
            try:
                config = cls.SECTION_CONFIG.get(section_key, {})
                raw_data = data.get(section_key)
                
                # Skip if data is None or empty, but don't crash
                if raw_data is not None and raw_data != {} and raw_data != []:
                    sections_html += cls._build_section(section_key, config, raw_data)
            except Exception as e:
                # Log error but continue with other sections
                sections_html += cls._build_error_section(section_key, str(e))
        
        return cls.HTML_TEMPLATE.format(
            header=header_html,
            content=sections_html
        )
    
    @classmethod
    def _extract_company_name(cls, data: Dict) -> str:
        """Extract company name from data safely."""
        try:
            for key in ["metadata", "info", "securityInfo"]:
                if key in data and isinstance(data[key], dict):
                    name = data[key].get("companyName") or data[key].get("symbol")
                    if name:
                        return name
        except:
            pass
        return "Unknown Company"
    
    @classmethod
    def _build_header(cls, symbol: str, company_name: str) -> str:
        """Build professional header."""
        return f"""
        <header class="header">
            <div class="header-content">
                <div class="symbol-badge">NSE EQ</div>
                <h1>{symbol.upper()}</h1>
                <div class="subtitle">{company_name}</div>
                <div class="timestamp">Report generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</div>
            </div>
        </header>
        """
    
    @classmethod
    def _build_section(cls, key: str, config: Dict, data: Any) -> str:
        """Build a section with appropriate layout."""
        try:
            title = config.get("title", cls._format_key(key))
            icon = config.get("icon", "📋")
            section_type = config.get("type", "dict")
            
            # Convert to appropriate format
            if section_type == "list" and isinstance(data, list):
                content_html = cls._build_list_cards(data, config)
            elif isinstance(data, dict):
                content_html = cls._build_dict_cards(data, config.get("priority", []))
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                content_html = cls._build_list_cards(data, config)
            else:
                content_html = cls._build_simple_card(data)
            
            return f"""
            <div class="section" id="section-{key}">
                <div class="section-header">
                    <div class="section-icon">{icon}</div>
                    <h2 class="section-title">{title}</h2>
                    <button class="section-toggle" aria-label="Toggle section">
                        <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </button>
                </div>
                <div class="section-body">
                    {content_html}
                </div>
            </div>
            """
        except Exception as e:
            return cls._build_error_section(key, str(e))
    
    @classmethod
    def _build_error_section(cls, key: str, error_msg: str) -> str:
        """Build an error display for a specific section."""
        return f"""
        <div class="section" id="section-{key}">
            <div class="section-header">
                <div class="section-icon">⚠️</div>
                <h2 class="section-title">{cls._format_key(key)} (Error)</h2>
            </div>
            <div class="section-body">
                <div class="empty-state" style="color: #e74c3c;">
                    <div class="empty-state-icon">❌</div>
                    <div>Failed to load: {error_msg}</div>
                </div>
            </div>
        </div>
        """
    
    @classmethod
    def _build_dict_cards(cls, data: Dict, priority_keys: list) -> str:
        """Build cards from dictionary data."""
        if not data or not isinstance(data, dict):
            return cls._empty_state()
        
        cards_html = '<div class="cards-grid">'
        
        # Priority keys first
        processed = set()
        for key in priority_keys:
            if key in data:
                try:
                    value = data[key]
                    cards_html += cls._create_card(key, value, highlight=True)
                    processed.add(key)
                except:
                    continue
        
        # Remaining keys
        for key, value in data.items():
            if key not in processed:
                try:
                    cards_html += cls._create_card(key, value)
                except:
                    continue
        
        cards_html += '</div>'
        return cards_html
    
    @classmethod
    def _build_list_cards(cls, data: list, config: Dict) -> str:
        """Build cards or table from list data."""
        if not data or not isinstance(data, list):
            return cls._empty_state()
        
        # If simple list of primitives
        if len(data) == 0:
            return cls._empty_state()
            
        if not isinstance(data[0], dict):
            return cls._build_dict_cards({"Items": ", ".join(map(str, data))}, [])
        
        # For list of dicts, create a responsive table/list view
        try:
            keys = list(data[0].keys())
            
            html = '<div class="list-card">'
            
            # Header
            html += '<div class="list-header">'
            for key in keys:
                html += f'<div>{cls._format_key(key)}</div>'
            html += '</div>'
            
            # Rows
            for item in data:
                html += '<div class="list-row">'
                for key in keys:
                    try:
                        value = item.get(key, "")
                        formatted = cls._format_value(value)
                        html += f'<div class="list-cell">{formatted}</div>'
                    except:
                        html += f'<div class="list-cell">-</div>'
                html += '</div>'
            
            html += '</div>'
            return html
        except:
            return cls._empty_state()
    
    @classmethod
    def _create_card(cls, key: str, value: Any, highlight: bool = False) -> str:
        """Create a single data card."""
        try:
            formatted_value = cls._format_value(value)
            value_class = "card-value"
            
            # Add styling based on value type/content
            if isinstance(value, (int, float)):
                value_class += " number"
                if key in ["change", "pChange"]:
                    if (isinstance(value, (int, float)) and value > 0) or (isinstance(value, str) and str(value).startswith('+')):
                        value_class += " positive"
                    elif (isinstance(value, (int, float)) and value < 0) or (isinstance(value, str) and str(value).startswith('-')):
                        value_class += " negative"
            
            highlight_class = " highlight" if highlight else ""
            
            return f"""
            <div class="card{highlight_class}">
                <div class="card-label">{cls._format_key(key)}</div>
                <div class="{value_class}">{formatted_value}</div>
            </div>
            """
        except Exception as e:
            return f"""
            <div class="card">
                <div class="card-label">{cls._format_key(key)}</div>
                <div class="card-value" style="color: #e74c3c;">Error: {str(e)}</div>
            </div>
            """
    
    @classmethod
    def _build_simple_card(cls, data: Any) -> str:
        """Build card for simple data types."""
        return f"""
        <div class="cards-grid">
            <div class="card highlight">
                <div class="card-label">Value</div>
                <div class="card-value">{cls._format_value(data)}</div>
            </div>
        </div>
        """
    
    @classmethod
    def _format_value(cls, value: Any) -> str:
        """Format value for display with appropriate badges."""
        try:
            if value is None or value == "":
                return '<span class="badge">N/A</span>'
            
            if isinstance(value, bool):
                status = "success" if value else "danger"
                text = "Yes" if value else "No"
                return f'<span class="badge {status}">{text}</span>'
            
            if isinstance(value, (int, float)):
                # Format numbers nicely
                if isinstance(value, float):
                    return f"{value:,.2f}"
                return f"{value:,}"
            
            if isinstance(value, str):
                # Check for status strings
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
        except:
            return '<span class="badge">Error</span>'
    
    @classmethod
    def _format_key(cls, key: str) -> str:
        """Format key name for display."""
        try:
            # Handle camelCase
            formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', key)
            # Handle snake_case
            formatted = formatted.replace('_', ' ')
            return formatted.title()
        except:
            return str(key)
    
    @classmethod
    def _empty_state(cls) -> str:
        """Return empty state HTML."""
        return """
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div>No data available for this section</div>
        </div>
        """
    
    @classmethod
    def _build_error_html(cls, symbol: str, message: str) -> str:
        """Build error page."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - {symbol}</title>
    <style>
        body {{ font-family: system-ui; background: #f5f5f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .error-container {{ text-align: center; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .error-icon {{ font-size: 48px; margin-bottom: 16px; }}
        h1 {{ color: #e74c3c; margin-bottom: 8px; }}
        .error-message {{ color: #666; margin-top: 16px; padding: 12px; background: #fee; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h1>Unable to Load Report</h1>
        <p>Symbol: <strong>{symbol.upper()}</strong></p>
        <div class="error-message">{message}</div>
    </div>
</body>
</html>"""


# Maintain original interface
def build_eq_html(symbol: str) -> str:
    """
    Build professional HTML equity report.
    
    Args:
        symbol: NSE stock symbol
        
    Returns:
        Complete HTML document as string
    """
    return EquityReportBuilder.build(symbol)
