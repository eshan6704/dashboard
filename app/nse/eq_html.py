from app.nse import nsepythonmodified as ns
import pandas as pd
from typing import Dict, Any, Optional


class EquityReportBuilder:
    """Professional HTML report generator for NSE equity data."""
    
    SECTION_ORDER = [
        "metadata",
        "securityInfo", 
        "priceInfo",
        "industryInfo",
        "pdSectorIndAll",
        "info",
        "preOpen",
        "preOpenMarket"
    ]
    
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equity Report - {symbol}</title>
    <style>
        :root {{
            --primary: #0b69a3;
            --primary-light: #0366d6;
            --bg: #f5f7fa;
            --card-bg: #ffffff;
            --border: #e1e4e8;
            --text: #24292e;
            --text-muted: #586069;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--primary);
        }}
        
        h1 {{
            color: var(--primary);
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        
        .timestamp {{
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }}
        
        .section {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
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
            font-weight: 600;
            font-size: 16px;
            color: var(--primary);
            text-transform: capitalize;
        }}
        
        .toggle-icon {{
            width: 20px;
            height: 20px;
            transition: transform 0.2s;
            color: var(--text-muted);
        }}
        
        .section.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        
        .section-body {{
            padding: 20px;
            overflow-x: auto;
        }}
        
        .section.collapsed .section-body {{
            display: none;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th {{
            background: var(--primary);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
        }}
        
        tr:hover td {{
            background: #f6f8fa;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: var(--text-muted);
            font-style: italic;
        }}
        
        .error-banner {{
            background: #ffeaea;
            border: 1px solid #ffcccc;
            color: #d32f2f;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 12px;
            }}
            
            .section-header {{
                padding: 12px 16px;
            }}
            
            .section-body {{
                padding: 12px;
            }}
            
            table {{
                font-size: 13px;
            }}
            
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Equity Report — {symbol}</h1>
            <div class="timestamp">Generated: {timestamp}</div>
        </header>
        {content}
    </div>
    
    <script>
        document.querySelectorAll('.section-header').forEach(header => {{
            header.addEventListener('click', () => {{
                header.parentElement.classList.toggle('collapsed');
            }});
        }});
    </script>
</body>
</html>"""
    
    @classmethod
    def build(cls, symbol: str) -> str:
        """
        Generate professional HTML equity report for given symbol.
        
        Args:
            symbol: NSE stock symbol
            
        Returns:
            Complete HTML document as string
        """
        from datetime import datetime
        
        # Fetch data
        try:
            data = ns.eq(symbol)
        except Exception as e:
            return cls._build_error_html(symbol, f"Failed to fetch data: {str(e)}")
        
        if not isinstance(data, dict):
            return cls._build_error_html(symbol, "Invalid data format received from API")
        
        # Build sections
        sections_html = ""
        for section_name in cls.SECTION_ORDER:
            df = cls._normalize_to_dataframe(data.get(section_name))
            sections_html += cls._build_section(section_name, df)
        
        return cls.HTML_TEMPLATE.format(
            symbol=symbol.upper(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content=sections_html
        )
    
    @classmethod
    def _normalize_to_dataframe(cls, value: Any) -> Optional[pd.DataFrame]:
        """Convert various data types to DataFrame."""
        if value is None:
            return None
            
        if isinstance(value, pd.DataFrame):
            return value
            
        if isinstance(value, list):
            return pd.DataFrame(value) if value else pd.DataFrame()
            
        if isinstance(value, dict):
            return pd.DataFrame([value])
            
        return pd.DataFrame()
    
    @classmethod
    def _build_section(cls, name: str, df: Optional[pd.DataFrame]) -> str:
        """Build HTML for a single section."""
        table_html = cls._dataframe_to_html(df) if df is not None and not df.empty else \
            '<div class="empty-state">No data available</div>'
        
        return f'''
        <div class="section">
            <div class="section-header">
                <span class="section-title">{cls._format_section_name(name)}</span>
                <svg class="toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="section-body">
                {table_html}
            </div>
        </div>'''
    
    @classmethod
    def _dataframe_to_html(cls, df: pd.DataFrame) -> str:
        """Convert DataFrame to styled HTML table."""
        return df.to_html(
            index=False,
            escape=False,
            border=0,
            classes="data-table",
            table_id=None
        )
    
    @classmethod
    def _format_section_name(cls, name: str) -> str:
        """Format camelCase/snake_case to readable title."""
        import re
        # Insert space before capital letters
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        return formatted.replace('_', ' ').title()
    
    @classmethod
    def _build_error_html(cls, symbol: str, message: str) -> str:
        """Build error page HTML."""
        from datetime import datetime
        return cls.HTML_TEMPLATE.format(
            symbol=symbol.upper(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content=f'<div class="error-banner">{message}</div>'
        )


# Convenience function maintaining original interface
def build_eq_html(symbol: str) -> str:
    """
    Build full HTML page for equity symbol output.
    
    Args:
        symbol: NSE stock symbol
        
    Returns:
        Complete HTML document as string
    """
    return EquityReportBuilder.build(symbol)
    