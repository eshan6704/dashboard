# app/gradio_frontend.py
"""
NSE Stock Dashboard - Modern Gradio 6.5+ Frontend
Connects to FastAPI backend with multiple deployment endpoints
"""

import gradio as gr
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import json
import re

# ============================================================
# API Configuration (from your index.html)
# ============================================================

API_ENDPOINTS = {
    "🚀 Replit": "https://hfapp--eshanpatel8.replit.app",
    "⏳ Render": "https://hfapp-jva5.onrender.com",
    "🤗 HF Space": "https://eshan6704-hfapp.hf.space",
    "🏠 Localhost": "http://localhost:8000"
}

# Default to localhost for local development, but allow switching
DEFAULT_ENDPOINT = "🏠 Localhost"

# ============================================================
# Request Type Definitions (from your router.py)
# ============================================================

REQ_TYPES = {
    "stock": [
        ("info", "Company Info"),
        ("intraday", "Intraday Data"),
        ("daily", "Daily Data"),
        ("nse_eq", "NSE Equity"),
        ("qresult", "Quarterly Results"),
        ("result", "Results"),
        ("balance", "Balance Sheet"),
        ("cashflow", "Cash Flow"),
        ("dividend", "Dividend History"),
        ("split", "Stock Splits"),
        ("other", "Other Data"),
        ("stock_hist", "Stock History")
    ],
    "index": [
        ("indices", "All Indices"),
        ("open", "Market Open"),
        ("preopen", "Pre-Open Data"),
        ("fno", "F&O Data"),
        ("fiidii", "FII/DII Data"),
        ("events", "Corporate Events"),
        ("index_highlow", "Index High/Low"),
        ("stock_highlow", "Stock High/Low"),
        ("bhav", "Bhavcopy"),
        ("largedeals", "Large Deals"),
        ("bulkdeals", "Bulk Deals"),
        ("blockdeals", "Block Deals"),
        ("most_active", "Most Active"),
        ("index_history", "Index History"),
        ("hlargedeals", "Historical Large Deals"),
        ("pe_pb", "P/E P/B Ratio"),
        ("total_returns", "Total Returns")
    ],
    "screener": [
        ("from_low", "From Low"),
        ("from_high", "From High"),
        ("volume", "Volume Leaders"),
        ("delivery", "Delivery Data")
    ]
}

DEFAULT_TYPES = {
    "stock": "info",
    "index": "indices",
    "screener": "from_low"
}

# ============================================================
# Helper Functions
# ============================================================

def get_fy_start() -> str:
    """Get current financial year start date (1st April)"""
    d = datetime.now()
    year = d.year if d.month >= 4 else d.year - 1
    return f"01-04-{year}"

def get_today() -> str:
    """Get today's date in DD-MM-YYYY format"""
    d = datetime.now()
    return f"{d.day:02d}-{d.month:02d}-{d.year}"

def build_filename(mode: str, req_type: str, name: str, end_date: str, start_date: str, suffix: str = "") -> str:
    """
    Build filename using same convention as router.py:
    @mode@req_type@name[@enddate@startdate@suffix].html
    """
    filename = f"@{mode}@{req_type}"
    if name:
        filename += f"@{name}"
    if end_date:
        filename += f"@{end_date}"
    if start_date:
        filename += f"@{start_date}"
    if suffix:
        filename += f"@{suffix}"
    return filename + ".html"

def parse_filename(filename: str) -> Dict[str, Any]:
    """Parse filename back to components"""
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("@")[1:]  # Remove leading empty
    
    result = {
        "mode": parts[0] if len(parts) > 0 else "",
        "req_type": parts[1] if len(parts) > 1 else "",
        "name": parts[2] if len(parts) > 2 else "",
        "end_date": parts[3] if len(parts) > 3 else "",
        "start_date": parts[4] if len(parts) > 4 else "",
        "suffix": parts[5] if len(parts) > 5 else ""
    }
    return result

def extract_tables_from_html(html_content: str) -> list:
    """Extract pandas DataFrames from HTML tables"""
    try:
        tables = pd.read_html(html_content)
        return tables
    except Exception:
        return []

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"

# ============================================================
# API Client
# ============================================================

class NSEApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NSE-Dashboard-Gradio/1.0"
        })
    
    def fetch_data(self, filename: str, force: bool = False) -> Tuple[str, str, Dict[str, Any]]:
        """
        Fetch data from FastAPI backend
        Returns: (html_content, status_message, metadata)
        """
        import time
        start_time = time.time()
        
        try:
            url = f"{self.base_url}/file"
            params = {"name": filename}
            if force:
                params["force"] = "true"
            
            response = self.session.get(url, params=params, timeout=30)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text
                size = len(content.encode('utf-8'))
                
                metadata = {
                    "status": "success",
                    "size_bytes": size,
                    "size_formatted": format_size(size),
                    "time_ms": round(elapsed * 1000, 1),
                    "filename": filename,
                    "url": response.url
                }
                
                status_msg = f"✅ Success | {metadata['size_formatted']} | {metadata['time_ms']}ms"
                return content, status_msg, metadata
            else:
                error_msg = f"HTTP {response.status_code}: {response.reason}"
                metadata = {
                    "status": "error",
                    "error": error_msg,
                    "time_ms": round(elapsed * 1000, 1)
                }
                return f"<pre>Error: {error_msg}</pre>", f"❌ {error_msg}", metadata
                
        except requests.exceptions.Timeout:
            return "<pre>Error: Request timeout (30s)</pre>", "❌ Timeout", {"status": "error"}
        except requests.exceptions.ConnectionError:
            return "<pre>Error: Cannot connect to backend</pre>", "❌ Connection Failed", {"status": "error"}
        except Exception as e:
            return f"<pre>Error: {str(e)}</pre>", f"❌ {str(e)}", {"status": "error", "error": str(e)}

# ============================================================
# Gradio 6.5+ UI Components
# ============================================================

def create_interface():
    """Create modern Gradio 6.5+ interface"""
    
    # Custom CSS for financial dashboard styling
    custom_css = """
    .financial-dashboard {
        font-family: 'Inter', system-ui, sans-serif;
    }
    .api-status-online { color: #10b981; font-weight: 600; }
    .api-status-offline { color: #ef4444; font-weight: 600; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .filename-tag {
        font-family: monospace;
        background: #f3f4f6;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
    """
    
    with gr.Blocks(
        title="NSE Stock Dashboard Pro",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="slate",
            neutral_hue="slate",
            font=["Inter", "system-ui", "sans-serif"],
            font_mono=["JetBrains Mono", "Consolas", "monospace"]
        ),
        css=custom_css,
        fill_width=True,
        fill_height=True
    ) as demo:
        
        # State management
        state_history = gr.State([])  # Store fetch history
        state_current_data = gr.State(None)
        state_metadata = gr.State({})
        
        # ==================== HEADER ====================
        with gr.Row():
            gr.Markdown("""
            # 📈 NSE Stock Dashboard Pro
            
            **Modern Gradio 6.5+ Interface** for FastAPI Backend | 
            [API Docs](http://localhost:8000/docs) | 
            [Original UI](http://localhost:8000/)
            """)
        
        # ==================== API SOURCE & STATUS ====================
        with gr.Row():
            with gr.Column(scale=2):
                api_source = gr.Dropdown(
                    label="🌐 API Source",
                    choices=list(API_ENDPOINTS.keys()),
                    value=DEFAULT_ENDPOINT,
                    allow_custom_value=True,  # Allow manual URL entry
                    filterable=True,
                    info="Select deployment target or enter custom URL"
                )
            
            with gr.Column(scale=1):
                api_status = gr.Textbox(
                    label="Status",
                    value="🟡 Ready",
                    interactive=False,
                    container=True
                )
            
            with gr.Column(scale=1):
                test_conn_btn = gr.Button("🔌 Test Connection", size="sm", variant="secondary")
        
        # ==================== MAIN INPUT PANEL ====================
        with gr.Row(equal_height=False):
            
            # ---- Left Column: Controls ----
            with gr.Column(scale=1, min_width=350):
                
                gr.Markdown("### 🔧 Request Configuration")
                
                # Mode Selection with Icons
                mode = gr.Radio(
                    label="Mode",
                    choices=["stock", "index", "screener"],
                    value="stock",
                    container=True
                )
                
                # Dynamic Type Selection (will be updated by mode)
                req_type = gr.Dropdown(
                    label="Request Type",
                    choices=[t[0] for t in REQ_TYPES["stock"]],
                    value="info",
                    allow_custom_value=False,
                    filterable=True,
                    info="Select data type to fetch"
                )
                
                # Symbol/Name Input with suggestions
                name = gr.Textbox(
                    label="Symbol / Index Name",
                    value="ITC",
                    placeholder="e.g., ITC, RELIANCE, NIFTY 50",
                    show_copy_button=True,
                    container=True
                )
                
                # Date Range
                with gr.Row():
                    date_end = gr.Textbox(
                        label="End Date",
                        value="",
                        placeholder="DD-MM-YYYY",
                        scale=1
                    )
                    date_start = gr.Textbox(
                        label="Start Date",
                        value="",
                        placeholder="DD-MM-YYYY",
                        scale=1
                    )
                
                # Auto-fill dates button
                with gr.Row():
                    btn_fy_dates = gr.Button("📅 FY Dates", size="sm", variant="secondary")
                    btn_today = gr.Button("📆 Today", size="sm", variant="secondary")
                    btn_clear_dates = gr.Button("❌ Clear", size="sm", variant="secondary")
                
                # Hidden suffix field (for advanced use)
                suffix = gr.Textbox(
                    label="Suffix (Advanced)",
                    value="",
                    visible=False
                )
                
                # Filename Preview (read-only)
                filename_preview = gr.Textbox(
                    label="Generated Filename",
                    value="",
                    interactive=False,
                    container=True,
                    elem_classes=["filename-tag"]
                )
                
                # Action Buttons
                with gr.Row():
                    btn_fetch = gr.Button(
                        "🚀 Fetch Data",
                        variant="primary",
                        size="lg",
                        scale=2
                    )
                    btn_clear = gr.Button(
                        "🗑️ Clear",
                        size="lg",
                        variant="stop",
                        scale=1
                    )
                
                # Options
                force_refresh = gr.Checkbox(
                    label="⚡ Force Refresh (ignore cache)",
                    value=False,
                    info="Regenerate file even if cached"
                )
                
                # Quick Presets Section
                gr.Markdown("### ⚡ Quick Presets")
                with gr.Row():
                    preset_itc = gr.Button("ITC Info", size="sm")
                    preset_reliance = gr.Button("RELIANCE", size="sm")
                    preset_nifty = gr.Button("NIFTY 50", size="sm")
                with gr.Row():
                    preset_fno = gr.Button("F&O Today", size="sm")
                    preset_fiidii = gr.Button("FII/DII", size="sm")
                    preset_preopen = gr.Button("Pre-Open", size="sm")
            
            # ---- Right Column: Output ----
            with gr.Column(scale=3):
                
                # Status Bar
                with gr.Row():
                    status_text = gr.Textbox(
                        label="Operation Status",
                        value="Ready to fetch data...",
                        interactive=False,
                        container=True
                    )
                
                # Output Tabs with Modern Components
                with gr.Tabs() as output_tabs:
                    
                    # Tab 1: Rendered HTML
                    with gr.TabItem("📊 Rendered View", id="rendered"):
                        html_output = gr.HTML(
                            label="Data Visualization",
                            container=True,
                            min_height=600,
                            show_label=False
                        )
                    
                    # Tab 2: Data Tables (Gradio 6.5 DataFrame)
                    with gr.TabItem("📋 Data Tables", id="tables"):
                        gr.Markdown("*Extracted tables from HTML response*")
                        tables_output = gr.Dataframe(
                            label="Table Data",
                            wrap=True,
                            show_label=False,
                            interactive=False,
                            height=600
                        )
                        table_count = gr.Textbox(
                            label="Tables Found",
                            value="0 tables",
                            interactive=False
                        )
                    
                    # Tab 3: Raw HTML
                    with gr.TabItem("📝 Raw HTML", id="raw"):
                        raw_output = gr.Code(
                            language="html",
                            label="HTML Source",
                            show_label=False,
                            min_height=600,
                            wrap_lines=True
                        )
                    
                    # Tab 4: JSON/Metadata
                    with gr.TabItem("🔍 Metadata", id="meta"):
                        metadata_json = gr.JSON(
                            label="Response Metadata",
                            show_label=False,
                            height=600
                        )
        
        # ==================== HISTORY PANEL ====================
        with gr.Accordion("📚 Fetch History", open=False):
            with gr.Row():
                btn_refresh_history = gr.Button("🔄 Refresh", size="sm")
                btn_clear_history = gr.Button("🗑️ Clear History", size="sm", variant="stop")
            
            history_list = gr.Dataframe(
                headers=["Time", "Source", "Filename", "Size", "Duration", "Status"],
                datatype=["str", "str", "str", "str", "str", "str"],
                label="Recent Fetches",
                wrap=True,
                height=300,
                interactive=False
            )
        
        # ==================== FOOTER ====================
        gr.Markdown("""
        ---
        **💡 Tips:** 
        • Press **Enter** in any field to fetch • 
        **FY Dates** auto-fills current financial year • 
        **Force Refresh** bypasses cache for live data
        """)
        
        # ============================================================
        # EVENT HANDLERS
        # ============================================================
        
        # ---- Update Request Types based on Mode ----
        def update_types(selected_mode: str):
            types = REQ_TYPES.get(selected_mode, [])
            choices = [t[0] for t in types]
            default = DEFAULT_TYPES.get(selected_mode, choices[0] if choices else "")
            return {
                req_type: gr.Dropdown(choices=choices, value=default),
                name: gr.update(value="ITC" if selected_mode == "stock" else 
                              ("NIFTY 50" if selected_mode == "index" else ""))
            }
        
        mode.change(
            update_types,
            inputs=mode,
            outputs=[req_type, name]
        )
        
        # ---- Update Filename Preview ----
        def update_filename(m, rt, n, de, ds, suf):
            fname = build_filename(m, rt, n, de, ds, suf)
            return fname
        
        for comp in [mode, req_type, name, date_end, date_start, suffix]:
            comp.change(
                update_filename,
                inputs=[mode, req_type, name, date_end, date_start, suffix],
                outputs=filename_preview
            )
        
        # ---- Date Helpers ----
        def set_fy_dates():
            return get_fy_start(), get_today()
        
        def set_today():
            return "", get_today()
        
        def clear_dates():
            return "", ""
        
        btn_fy_dates.click(set_fy_dates, outputs=[date_start, date_end])
        btn_today.click(set_today, outputs=[date_start, date_end])
        btn_clear_dates.click(clear_dates, outputs=[date_start, date_end])
        
        # ---- Main Fetch Function ----
        def fetch_data(api_src, m, rt, n, de, ds, suf, force):
            base_url = API_ENDPOINTS.get(api_src, api_src)
            client = NSEApiClient(base_url)
            
            filename = build_filename(m, rt, n, de, ds, suf)
            
            # Update status
            yield {
                status_text: "⏳ Fetching...",
                html_output: "<div style='text-align:center; padding:40px;'>🔄 Loading...</div>",
                raw_output: "",
                tables_output: pd.DataFrame(),
                metadata_json: {"fetching": True},
                api_status: "🟡 Fetching..."
            }
            
            # Perform fetch
            content, status_msg, meta = client.fetch_data(filename, force)
            
            # Extract tables
            tables = extract_tables_from_html(content)
            
            # Prepare table display (combine all tables or show first)
            if tables:
                display_df = tables[0] if len(tables) == 1 else pd.concat(tables, ignore_index=True)
                table_info = f"{len(tables)} table(s), {len(display_df)} rows"
            else:
                display_df = pd.DataFrame({"Info": ["No tables found in response"]})
                table_info = "0 tables"
            
            # Build history entry
            history_entry = {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Source": api_src,
                "Filename": filename,
                "Size": meta.get("size_formatted", "N/A"),
                "Duration": f"{meta.get('time_ms', 0)}ms",
                "Status": "✅" if meta.get("status") == "success" else "❌"
            }
            
            result = {
                status_text: status_msg,
                html_output: content if meta.get("status") == "success" else f"<pre>{content}</pre>",
                raw_output: content,
                tables_output: display_df,
                table_count: table_info,
                metadata_json: meta,
                api_status: "🟢 Online" if meta.get("status") == "success" else "🔴 Error",
                state_current_data: content,
                state_metadata: meta
            }
            
            # Update history
            yield result
        
        btn_fetch.click(
            fetch_data,
            inputs=[api_source, mode, req_type, name, date_end, date_start, suffix, force_refresh],
            outputs=[
                status_text, html_output, raw_output, tables_output, 
                table_count, metadata_json, api_status, state_current_data, state_metadata
            ]
        )
        
        # ---- Clear Function ----
        def clear_all():
            return {
                html_output: "<div style='text-align:center; padding:40px; color:#9ca3af;'>"
                           "<div style='font-size:48px; margin-bottom:16px;'>📈</div>"
                           "<p>Ready to fetch data...</p></div>",
                raw_output: "",
                tables_output: pd.DataFrame(),
                table_count: "0 tables",
                metadata_json: {},
                status_text: "Ready",
                state_current_data: None,
                state_metadata: {}
            }
        
        btn_clear.click(
            clear_all,
            outputs=[
                html_output, raw_output, tables_output, table_count,
                metadata_json, status_text, state_current_data, state_metadata
            ]
        )
        
        # ---- Test Connection ----
        def test_connection(api_src):
            base_url = API_ENDPOINTS.get(api_src, api_src)
            try:
                resp = requests.get(f"{base_url}/", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    return f"🟢 Online | {data.get('service', 'Backend OK')}"
                return f"🟡 HTTP {resp.status_code}"
            except Exception as e:
                return f"🔴 Offline | {str(e)[:50]}"
        
        test_conn_btn.click(
            test_connection,
            inputs=api_source,
            outputs=api_status
        )
        
        # ---- Quick Presets ----
        def preset_stock_info(symbol):
            return "stock", "info", symbol, "", ""
        
        def preset_index_open(idx_name):
            return "index", "open", idx_name, "", ""
        
        def preset_fno_data():
            today = get_today()
            return "index", "fno", "", today, ""
        
        def preset_fiidii_data():
            return "index", "fiidii", "", "", ""
        
        def preset_preopen_data():
            return "index", "preopen", "NIFTY 50", "", ""
        
        preset_itc.click(
            lambda: ("stock", "info", "ITC", "", ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        preset_reliance.click(
            lambda: ("stock", "info", "RELIANCE", "", ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        preset_nifty.click(
            lambda: ("index", "indices", "NIFTY 50", "", ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        preset_fno.click(
            lambda: ("index", "fno", "", get_today(), ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        preset_fiidii.click(
            lambda: ("index", "fiidii", "", "", ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        preset_preopen.click(
            lambda: ("index", "preopen", "NIFTY 50", "", ""),
            outputs=[mode, req_type, name, date_end, date_start]
        )
        
        # ---- Keyboard Shortcuts (via JS) ----
        demo.load(
            None,
            None,
            js="""
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
                    document.querySelector('button.primary').click();
                }
                if (e.key === 'Escape') {
                    document.querySelector('button[variant="stop"]').click();
                }
            });
            """
        )
    
    return demo

# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    demo = create_interface()
    
    # Gradio 6.5+ launch configuration
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,           # Local only, set True for public URL
        show_error=True,
        quiet=False,
        favicon_path=None,     # Could add custom favicon
        show_api=False,        # Don't show internal API docs
        allowed_paths=[],      # Restrict file access
        blocked_paths=["/data/files"],  # Protect data directory
        root_path=None,
        app_kwargs={
            "docs_url": None,  # Disable FastAPI docs for Gradio app
            "redoc_url": None
        }
    )
