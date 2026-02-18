from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import gradio as gr
import requests
import pandas as pd
from datetime import datetime
import os

# -------------------------------------------------------
# Router
# -------------------------------------------------------
from app.router.router import router

# -------------------------------------------------------
# FastAPI app
# -------------------------------------------------------
app = FastAPI(title="Stock / Index Backend")

# -------------------------------------------------------
# Middleware
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# -------------------------------------------------------
# API Routes
# -------------------------------------------------------
app.include_router(router)

# -------------------------------------------------------
# Gradio UI
# -------------------------------------------------------

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

# -------------------------------------------------------
# Gradio Interface (Gradio 6.0+ compatible)
# -------------------------------------------------------

with gr.Blocks(title="NSE Stock Dashboard") as demo:
    
    gr.Markdown("# 📈 NSE Stock Dashboard")
    
    with gr.Row():
        # Left panel - Controls
        with gr.Column(scale=1):
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
            
            name = gr.Textbox(label="Symbol/Name", value="ITC")
            
            with gr.Row():
                date_end = gr.Textbox(label="End Date", placeholder="DD-MM-YYYY")
                date_start = gr.Textbox(label="Start Date", placeholder="DD-MM-YYYY")
            
            with gr.Row():
                btn_fy = gr.Button("📅 FY", size="sm")
                btn_today = gr.Button("📆 Today", size="sm")
            
            force = gr.Checkbox(label="⚡ Force Refresh", value=False)
            
            with gr.Row():
                btn_fetch = gr.Button("🚀 Fetch", variant="primary")
                btn_clear = gr.Button("🗑️ Clear")
            
            gr.Markdown("### ⚡ Presets")
            with gr.Row():
                p1 = gr.Button("ITC", size="sm")
                p2 = gr.Button("RELIANCE", size="sm")
                p3 = gr.Button("NIFTY", size="sm")
        
        # Right panel - Output
        with gr.Column(scale=3):
            status = gr.Textbox(label="Status", value="Ready", interactive=False)
            
            with gr.Tabs():
                with gr.TabItem("📊 Rendered"):
                    html_out = gr.HTML()
                with gr.TabItem("📋 Table"):
                    # No height parameter in Gradio 6.0+
                    table_out = gr.DataFrame()
                with gr.TabItem("📝 Raw"):
                    raw_out = gr.Code(language="html")
    
    # Events
    mode.change(
        lambda m: gr.Dropdown(choices=REQ_TYPES[m], value=DEFAULT_TYPES[m]),
        inputs=mode,
        outputs=req_type
    )
    
    btn_fy.click(lambda: (get_fy_start(), get_today()), outputs=[date_start, date_end])
    btn_today.click(lambda: ("", get_today()), outputs=[date_start, date_end])
    
    def do_fetch(m, rt, n, de, ds, f):
        filename = build_filename(m, rt, n, de, ds)
        yield {
            status: f"Fetching {filename}...",
            html_out: "<div style='text-align:center;padding:40px;'>🔄 Loading...</div>",
            raw_out: "",
            table_out: pd.DataFrame()
        }
        
        result = fetch_data_internal(filename, f)
        
        if result["success"]:
            tables = extract_tables(result["content"])
            yield {
                status: f"✅ Success ({result['size']} chars)",
                html_out: result["content"],
                raw_out: result["content"],
                table_out: tables
            }
        else:
            yield {
                status: f"❌ {result['error']}",
                html_out: f"<pre>Error: {result['error']}</pre>",
                raw_out: str(result),
                table_out: pd.DataFrame({"Error": [result["error"]]})
            }
    
    btn_fetch.click(
        do_fetch,
        inputs=[mode, req_type, name, date_end, date_start, force],
        outputs=[status, html_out, raw_out, table_out]
    )
    
    def clear_all():
        return {
            status: "Ready",
            html_out: "<div style='text-align:center;padding:40px;color:#9ca3af;'><div style='font-size:48px;'>📈</div><p>Ready</p></div>",
            raw_out: "",
            table_out: pd.DataFrame()
        }
    
    btn_clear.click(clear_all, outputs=[status, html_out, raw_out, table_out])
    
    # Presets
    p1.click(lambda: ("stock", "info", "ITC", "", ""), outputs=[mode, req_type, name, date_end, date_start])
    p2.click(lambda: ("stock", "info", "RELIANCE", "", ""), outputs=[mode, req_type, name, date_end, date_start])
    p3.click(lambda: ("index", "indices", "NIFTY 50", "", ""), outputs=[mode, req_type, name, date_end, date_start])

# Mount at root
app = gr.mount_gradio_app(app, demo, path="/")