"""
Gradio UI for NSE Stock Dashboard
Collapsible sidebar - minimizes but keeps functionality accessible
"""

import gradio as gr
import requests
import pandas as pd
from datetime import datetime


REQ_TYPES = {
    "stock": ['info','intraday','daily','nse_eq','qresult','result','balance','cashflow','dividend','split','other','stock_hist'],
    "index": ['indices','open','preopen','fno','fiidii','events','index_highlow','stock_highlow','bhav','largedeals','bulkdeals','blockdeals','most_active','index_history','hlargedeals','pe_pb','total_returns'],
    "screener": ['from_low','from_high','volume','delivery']
}

DEFAULT_TYPES = {"stock": "info", "index": "indices", "screener": "from_low"}


def get_fy_start():
    d = datetime.now()
    year = d.year if d.month >= 4 else d.year - 1
    return f"01-04-{year}"


def get_today():
    d = datetime.now()
    return f"{d.day:02d}-{d.month:02d}-{d.year}"


def build_filename(mode, req_type, name, end_date, start_date, suffix=""):
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


def fetch_data_internal(filename, force=False):
    try:
        base_url = "http://localhost:7860"
        url = f"{base_url}/file"
        params = {"name": filename}
        if force:
            params["force"] = "true"
        
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return {"success": True, "content": resp.text, "size": len(resp.text)}
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_tables(html_content):
    try:
        tables = pd.read_html(html_content)
        if tables:
            if len(tables) == 1:
                return tables[0]
            else:
                return pd.concat(tables, ignore_index=True)
    except Exception:
        pass
    return pd.DataFrame({"Info": ["No tables found"]})


def create_interface():
    with gr.Blocks(title="NSE Stock Dashboard") as demo:
        
        gr.Markdown("# 📈 NSE Stock Dashboard")
        
        # State to track sidebar collapse
        is_collapsed = gr.State(False)
        
        with gr.Row():
            
            # ==========================================
            # LEFT SIDEBAR (Collapsible)
            # ==========================================
            
            # Expanded sidebar
            with gr.Column(scale=1, min_width=280, visible=True) as sidebar_expanded:
                
                gr.Markdown("### 🔧 Request")
                
                mode = gr.Radio(
                    label="Mode",
                    choices=["stock", "index", "screener"],
                    value="stock"
                )
                
                req_type = gr.Dropdown(
                    label="Type",
                    choices=REQ_TYPES["stock"],
                    value="info"
                )
                
                name = gr.Textbox(
                    label="Symbol/Name",
                    value="ITC",
                    placeholder="e.g., ITC, RELIANCE, NIFTY 50"
                )
                
                with gr.Row():
                    date_end = gr.Textbox(label="End Date", placeholder="DD-MM-YYYY", scale=1)
                    date_start = gr.Textbox(label="Start Date", placeholder="DD-MM-YYYY", scale=1)
                
                with gr.Row():
                    btn_fy = gr.Button("📅 FY", size="sm")
                    btn_today = gr.Button("📆 Today", size="sm")
                
                force = gr.Checkbox(label="⚡ Force Refresh", value=False)
                
                with gr.Row():
                    btn_fetch = gr.Button("🚀 Fetch", variant="primary", scale=2)
                    btn_clear = gr.Button("🗑️ Clear", scale=1)
                
                # Collapse button at bottom
                gr.Markdown("---")
                btn_collapse = gr.Button("◀ Collapse", size="sm", variant="secondary")
            
            # Collapsed sidebar (icon only)
            with gr.Column(scale=0, min_width=50, visible=False) as sidebar_collapsed:
                gr.Markdown("### ☰")
                btn_expand = gr.Button("☰", size="lg", variant="primary")
                gr.Markdown("<div style='writing-mode: vertical-rl; text-orientation: mixed; font-size: 12px; color: #666; padding: 10px 0;'>Controls</div>")
            
            # ==========================================
            # RIGHT CONTENT AREA
            # ==========================================
            
            with gr.Column(scale=4) as content_area:
                
                status = gr.Textbox(label="Status", value="Ready to fetch data...", interactive=False)
                
                with gr.Tabs():
                    with gr.TabItem("📊 Rendered"):
                        html_out = gr.HTML()
                    with gr.TabItem("📋 Table"):
                        table_out = gr.DataFrame()
                    with gr.TabItem("📝 Raw"):
                        raw_out = gr.Code(language="html")
        
        # ==========================================
        # EVENT HANDLERS
        # ==========================================
        
        # Update request types when mode changes
        mode.change(
            lambda m: gr.Dropdown(choices=REQ_TYPES[m], value=DEFAULT_TYPES[m]),
            inputs=mode,
            outputs=req_type
        )
        
        # Date helpers
        btn_fy.click(lambda: (get_fy_start(), get_today()), outputs=[date_start, date_end])
        btn_today.click(lambda: ("", get_today()), outputs=[date_start, date_end])
        
        # COLLAPSE sidebar
        def collapse_sidebar():
            return {
                sidebar_expanded: gr.Column(visible=False),
                sidebar_collapsed: gr.Column(visible=True),
                content_area: gr.Column(scale=5),
                is_collapsed: True
            }
        
        btn_collapse.click(
            collapse_sidebar,
            outputs=[sidebar_expanded, sidebar_collapsed, content_area, is_collapsed]
        )
        
        # EXPAND sidebar
        def expand_sidebar():
            return {
                sidebar_expanded: gr.Column(visible=True),
                sidebar_collapsed: gr.Column(visible=False),
                content_area: gr.Column(scale=4),
                is_collapsed: False
            }
        
        btn_expand.click(
            expand_sidebar,
            outputs=[sidebar_expanded, sidebar_collapsed, content_area, is_collapsed]
        )
        
        # FETCH data (auto-collapse after fetch)
        def on_fetch(m, rt, n, de, ds, f, collapsed):
            filename = build_filename(m, rt, n, de, ds)
            
            # Show loading
            yield {
                status: f"⏳ Fetching: {filename}",
                html_out: "<div style='text-align:center;padding:40px;'>🔄 Loading...</div>",
                raw_out: "",
                table_out: pd.DataFrame()
            }
            
            # Fetch
            result = fetch_data_internal(filename, f)
            
            # Prepare outputs
            if result["success"]:
                tables = extract_tables(result["content"])
                outputs = {
                    status: f"✅ Success | {result['size']:,} chars",
                    html_out: result["content"],
                    raw_out: result["content"],
                    table_out: tables
                }
            else:
                outputs = {
                    status: f"❌ Error: {result['error']}",
                    html_out: f"<pre style='color:red'>Error: {result['error']}</pre>",
                    raw_out: str(result),
                    table_out: pd.DataFrame({"Error": [result["error"]]})
                }
            
            # Auto-collapse if not already collapsed
            if not collapsed:
                outputs.update({
                    sidebar_expanded: gr.Column(visible=False),
                    sidebar_collapsed: gr.Column(visible=True),
                    content_area: gr.Column(scale=5),
                    is_collapsed: True
                })
            
            yield outputs
        
        btn_fetch.click(
            on_fetch,
            inputs=[mode, req_type, name, date_end, date_start, force, is_collapsed],
            outputs=[status, html_out, raw_out, table_out, sidebar_expanded, sidebar_collapsed, content_area, is_collapsed]
        )
        
        # CLEAR (restore sidebar to expanded)
        def on_clear():
            return {
                status: "Ready",
                html_out: "<div style='text-align:center;padding:40px;color:#9ca3af;'><div style='font-size:48px;'>📈</div><p>Ready to fetch data...</p></div>",
                raw_out: "",
                table_out: pd.DataFrame(),
                sidebar_expanded: gr.Column(visible=True),
                sidebar_collapsed: gr.Column(visible=False),
                content_area: gr.Column(scale=4),
                is_collapsed: False
            }
        
        btn_clear.click(
            on_clear,
            outputs=[status, html_out, raw_out, table_out, sidebar_expanded, sidebar_collapsed, content_area, is_collapsed]
        )
    
    return demo