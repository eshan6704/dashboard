"""
Gradio UI for NSE Stock Dashboard
Separated from FastAPI app
"""

import gradio as gr
import requests
import pandas as pd
from datetime import datetime


# Configuration
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
    """Call own API internally"""
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
    """Extract tables using pandas"""
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
    """Create and return Gradio interface"""
    
    with gr.Blocks(title="NSE Stock Dashboard") as demo:
        
        gr.Markdown("# 📈 NSE Stock Dashboard")
        
        # State to track if sidebar is minimized
        sidebar_state = gr.State(False)
        
        with gr.Row():
            # Left panel - Controls (will be minimized after fetch)
            with gr.Column(scale=1, min_width=250) as left_panel:
                
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
                    date_end = gr.Textbox(
                        label="End Date",
                        placeholder="DD-MM-YYYY",
                        scale=1
                    )
                    date_start = gr.Textbox(
                        label="Start Date",
                        placeholder="DD-MM-YYYY",
                        scale=1
                    )
                
                with gr.Row():
                    btn_fy = gr.Button("📅 FY", size="sm")
                    btn_today = gr.Button("📆 Today", size="sm")
                
                force = gr.Checkbox(
                    label="⚡ Force Refresh",
                    value=False
                )
                
                with gr.Row():
                    btn_fetch = gr.Button("🚀 Fetch", variant="primary", scale=2)
                    btn_clear = gr.Button("🗑️ Clear", scale=1)
                
                # Toggle button to restore sidebar
                btn_toggle_sidebar = gr.Button("☰ Show Controls", size="sm", visible=False)
            
            # Right panel - Output
            with gr.Column(scale=3) as right_panel:
                
                status = gr.Textbox(
                    label="Status",
                    value="Ready to fetch data...",
                    interactive=False
                )
                
                with gr.Tabs():
                    with gr.TabItem("📊 Rendered"):
                        html_out = gr.HTML()
                    
                    with gr.TabItem("📋 Table"):
                        table_out = gr.DataFrame()
                    
                    with gr.TabItem("📝 Raw"):
                        raw_out = gr.Code(language="html")
        
        # Event: Update request types when mode changes
        mode.change(
            lambda m: gr.Dropdown(choices=REQ_TYPES[m], value=DEFAULT_TYPES[m]),
            inputs=mode,
            outputs=req_type
        )
        
        # Event: Date helpers
        btn_fy.click(
            lambda: (get_fy_start(), get_today()),
            outputs=[date_start, date_end]
        )
        
        btn_today.click(
            lambda: ("", get_today()),
            outputs=[date_start, date_end]
        )
        
        # Event: Fetch data with sidebar minimization
        def on_fetch(m, rt, n, de, ds, f):
            filename = build_filename(m, rt, n, de, ds)
            
            # First yield: loading state + minimize sidebar
            yield {
                status: f"⏳ Fetching: {filename}",
                html_out: "<div style='text-align:center;padding:40px;'>🔄 Loading...</div>",
                raw_out: "",
                table_out: pd.DataFrame(),
                # Minimize left panel, expand right panel
                left_panel: gr.Column(scale=1, min_width=80, visible=False),
                right_panel: gr.Column(scale=10),
                btn_toggle_sidebar: gr.Button(visible=True)
            }
            
            # Fetch data
            result = fetch_data_internal(filename, f)
            
            if result["success"]:
                tables = extract_tables(result["content"])
                yield {
                    status: f"✅ Success | {result['size']:,} chars",
                    html_out: result["content"],
                    raw_out: result["content"],
                    table_out: tables,
                    left_panel: gr.Column(scale=1, min_width=80, visible=False),
                    right_panel: gr.Column(scale=10),
                    btn_toggle_sidebar: gr.Button(visible=True)
                }
            else:
                yield {
                    status: f"❌ Error: {result['error']}",
                    html_out: f"<pre style='color:red'>Error: {result['error']}</pre>",
                    raw_out: str(result),
                    table_out: pd.DataFrame({"Error": [result["error"]]}),
                    left_panel: gr.Column(scale=1, min_width=80, visible=False),
                    right_panel: gr.Column(scale=10),
                    btn_toggle_sidebar: gr.Button(visible=True)
                }
        
        btn_fetch.click(
            on_fetch,
            inputs=[mode, req_type, name, date_end, date_start, force],
            outputs=[status, html_out, raw_out, table_out, left_panel, right_panel, btn_toggle_sidebar]
        )
        
        # Event: Clear with sidebar restore
        def on_clear():
            return {
                status: "Ready",
                html_out: "<div style='text-align:center;padding:40px;color:#9ca3af;'><div style='font-size:48px;'>📈</div><p>Ready to fetch data...</p></div>",
                raw_out: "",
                table_out: pd.DataFrame(),
                left_panel: gr.Column(scale=1, min_width=250, visible=True),
                right_panel: gr.Column(scale=3),
                btn_toggle_sidebar: gr.Button(visible=False)
            }
        
        btn_clear.click(
            on_clear,
            outputs=[status, html_out, raw_out, table_out, left_panel, right_panel, btn_toggle_sidebar]
        )
        
        # Event: Toggle sidebar manually
        def toggle_sidebar():
            # This will restore the sidebar
            return {
                left_panel: gr.Column(scale=1, min_width=250, visible=True),
                right_panel: gr.Column(scale=3),
                btn_toggle_sidebar: gr.Button(visible=False)
            }
        
        btn_toggle_sidebar.click(
            toggle_sidebar,
            outputs=[left_panel, right_panel, btn_toggle_sidebar]
        )
    
    return demo