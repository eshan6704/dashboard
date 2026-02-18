"""
Gradio UI for NSE Stock Dashboard
Sticky top bar with collapsible controls, smart dates
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
    """Current financial year start (1st April)"""
    d = datetime.now()
    year = d.year if d.month >= 4 else d.year - 1
    return f"01-04-{year}"


def get_today():
    """Today's date in DD-MM-YYYY"""
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
            return pd.concat(tables, ignore_index=True)
    except Exception:
        pass
    return pd.DataFrame({"Info": ["No tables found"]})


def create_interface():
    with gr.Blocks(
        title="NSE Stock Dashboard",
        css="""
        .top-bar { 
            position: sticky; 
            top: 0; 
            z-index: 100; 
            background: white; 
            border-bottom: 1px solid #e5e7eb;
            padding: 8px 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .compact-row { 
            display: flex; 
            gap: 8px; 
            align-items: center;
            flex-wrap: wrap;
        }
        .status-badge {
            background: #f3f4f6;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-left: auto;
        }

        .status-fetching { background: #dbeafe; color: #1e40af; }
        .status-success { background: #d1fae5; color: #065f46; }
        .status-error { background: #fee2e2; color: #991b1b; }
        .hidden-field { display: none !important; }
        """
    ) as demo:
        
        # ==========================================
        # STICKY TOP BAR (Always visible)
        # ==========================================
        
        with gr.Row(elem_classes="top-bar"):
            with gr.Column(scale=1):
                with gr.Row(elem_classes="compact-row"):
                    # Mode
                    mode = gr.Dropdown(
                        label=None,
                        choices=["stock", "index", "screener"],
                        value="stock",
                        show_label=False,
                        container=False,
                        min_width=80
                    )
                    
                    # Type
                    req_type = gr.Dropdown(
                        label=None,
                        choices=REQ_TYPES["stock"],
                        value="info",
                        show_label=False,
                        container=False,
                        min_width=120
                    )
                    
                    # Symbol
                    name = gr.Textbox(
                        label=None,
                        value="ITC",
                        placeholder="Symbol",
                        show_label=False,
                        container=False,
                        min_width=100
                    )
                    
                    # End Date (visible, prefilled today, user can change)
                    date_end = gr.Textbox(
                        label=None,
                        value=get_today(),
                        placeholder="End Date",
                        show_label=False,
                        container=False,
                        min_width=100
                    )
                    
                    # Start Date (HIDDEN - fixed to FY start)
                    date_start = gr.Textbox(
                        label=None,
                        value=get_fy_start(),
                        show_label=False,
                        container=False,
                        elem_classes="hidden-field"
                    )
                    
                    # Force refresh
                    force = gr.Checkbox(
                        label="Force",
                        value=False,
                        container=False,
                        min_width=60
                    )
                    
                    # Fetch button
                    btn_fetch = gr.Button("🚀 Fetch", variant="primary", min_width=80)
                    
                    # Clear button
                    btn_clear = gr.Button("🗑️", min_width=40)
                    
                    # Status (right side)
                    status = gr.Textbox(
                        label=None,
                        value="Ready",
                        show_label=False,
                        container=False,
                        interactive=False,
                        elem_classes="status-badge",
                        min_width=150
                    )
        
        # ==========================================
        # MAIN CONTENT AREA
        # ==========================================
        
        with gr.Row():
            with gr.Column(scale=1):
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
        
        # Update types when mode changes
        mode.change(
            lambda m: gr.Dropdown(choices=REQ_TYPES[m], value=DEFAULT_TYPES[m]),
            inputs=mode,
            outputs=req_type
        )
        
        # Update defaults when mode changes
        def update_defaults(m):
            if m == "stock":
                return "ITC"
            elif m == "index":
                return "NIFTY 50"
            return ""
        
        mode.change(update_defaults, inputs=mode, outputs=name)
        
        # Fetch data
        def on_fetch(m, rt, n, de, ds, f):
            filename = build_filename(m, rt, n, de, ds)
            
            # Loading state
            yield {
                status: gr.Textbox(value="⏳ Fetching...", elem_classes="status-badge status-fetching"),
                html_out: "<div style='text-align:center;padding:60px;'><div style='font-size:48px;'>🔄</div><p>Loading data...</p></div>",
                raw_out: "",
                table_out: pd.DataFrame()
            }
            
            # Fetch
            result = fetch_data_internal(filename, f)
            
            if result["success"]:
                tables = extract_tables(result["content"])
                yield {
                    status: gr.Textbox(value=f"✅ {result['size']:,} chars", elem_classes="status-badge status-success"),
                    html_out: result["content"],
                    raw_out: result["content"],
                    table_out: tables
                }
            else:
                yield {
                    status: gr.Textbox(value=f"❌ {result['error'][:30]}", elem_classes="status-badge status-error"),
                    html_out: f"<pre style='color:red;padding:20px;'>Error: {result['error']}</pre>",
                    raw_out: str(result),
                    table_out: pd.DataFrame({"Error": [result["error"]]})
                }
        
        btn_fetch.click(
            on_fetch,
            inputs=[mode, req_type, name, date_end, date_start, force],
            outputs=[status, html_out, raw_out, table_out]
        )
        
        # Clear
        def on_clear():
            return {
                status: gr.Textbox(value="Ready", elem_classes="status-badge"),
                html_out: "<div style='text-align:center;padding:60px;color:#9ca3af;'><div style='font-size:64px;'>📈</div><p>Ready to fetch data...</p></div>",
                raw_out: "",
                table_out: pd.DataFrame()
            }
        
        btn_clear.click(on_clear, outputs=[status, html_out, raw_out, table_out])
    
    return demo