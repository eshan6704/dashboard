# app/gradio_frontend.py
"""
NSE Stock Dashboard - LOCAL Gradio Frontend
Runs on your machine, connects to cloud FastAPI backend
"""

import gradio as gr
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import os

# ============================================================
# API Configuration - Your Cloud Deployments
# ============================================================

API_ENDPOINTS = {
    "🤗 HuggingFace": "https://eshan6704-hfapp.hf.space",
    "🚀 Replit": "https://hfapp--eshanpatel8.replit.app",
    "⏳ Render": "https://hfapp-jva5.onrender.com",
    "🏠 Local Test": "http://localhost:8000"
}

# Request Types (from your router.py)
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
    if name: filename += f"@{name}"
    if end_date: filename += f"@{end_date}"
    if start_date: filename += f"@{start_date}"
    if suffix: filename += f"@{suffix}"
    return filename + ".html"

def fetch_from_api(base_url, filename, force=False):
    """Fetch data from cloud API"""
    try:
        url = f"{base_url}/file"
        params = {"name": filename}
        if force: params["force"] = "true"
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code == 200:
            return {
                "success": True,
                "content": resp.text,
                "size": len(resp.text),
                "status": f"✅ Success ({len(resp.text)} chars)"
            }
        else:
            return {
                "success": False,
                "content": f"<pre>Error: HTTP {resp.status_code}</pre>",
                "status": f"❌ HTTP {resp.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "content": f"<pre>Error: {str(e)}</pre>",
            "status": f"❌ {str(e)[:50]}"
        }

def extract_tables(html_content):
    try:
        tables = pd.read_html(html_content)
        if tables:
            return pd.concat(tables, ignore_index=True) if len(tables) > 1 else tables[0]
    except:
        pass
    return pd.DataFrame({"Message": ["No tables found or parse error"]})

# ============================================================
# GRADIO UI
# ============================================================

with gr.Blocks(
    title="NSE Stock Dashboard Pro",
    theme=gr.themes.Soft(primary_hue="indigo"),
    fill_width=True
) as demo:
    
    gr.Markdown("""
    # 📈 NSE Stock Dashboard Pro
    **Local Gradio Frontend** → Connects to Cloud FastAPI Backend
    """)
    
    # API Source Selection
    with gr.Row():
        api_source = gr.Dropdown(
            label="🌐 Select API Source",
            choices=list(API_ENDPOINTS.keys()),
            value="🤗 HuggingFace",
            allow_custom_value=True
        )
        conn_status = gr.Textbox(label="Status", value="Ready", interactive=False)
    
    # Main Controls
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔧 Request")
            
            mode = gr.Radio(label="Mode", choices=["stock", "index", "screener"], value="stock")
            req_type = gr.Dropdown(label="Type", choices=REQ_TYPES["stock"], value="info")
            name = gr.Textbox(label="Symbol/Name", value="ITC", placeholder="ITC, RELIANCE, NIFTY 50...")
            
            with gr.Row():
                date_end = gr.Textbox(label="End Date", placeholder="DD-MM-YYYY")
                date_start = gr.Textbox(label="Start Date", placeholder="DD-MM-YYYY")
            
            # Quick buttons
            with gr.Row():
                btn_fy = gr.Button("📅 FY", size="sm")
                btn_today = gr.Button("📆 Today", size="sm")
            
            force = gr.Checkbox(label="⚡ Force Refresh", value=False)
            
            with gr.Row():
                btn_fetch = gr.Button("🚀 Fetch", variant="primary", scale=2)
                btn_clear = gr.Button("🗑️ Clear", variant="stop", scale=1)
            
            # Presets
            gr.Markdown("### ⚡ Presets")
            with gr.Row():
                p1 = gr.Button("ITC", size="sm")
                p2 = gr.Button("RELIANCE", size="sm")
                p3 = gr.Button("NIFTY", size="sm")
            with gr.Row():
                p4 = gr.Button("F&O", size="sm")
                p5 = gr.Button("FII/DII", size="sm")
        
        with gr.Column(scale=3):
            status = gr.Textbox(label="Result", value="Ready to fetch...", interactive=False)
            
            with gr.Tabs():
                with gr.TabItem("📊 Rendered"):
                    html_out = gr.HTML(show_label=False, min_height=500)
                with gr.TabItem("📋 Table"):
                    table_out = gr.DataFrame(show_label=False, interactive=False, height=500)
                with gr.TabItem("📝 Raw"):
                    raw_out = gr.Code(language="html", show_label=False, min_height=500)
    
    # Events
    def update_types(m):
        return gr.Dropdown(choices=REQ_TYPES[m], value=DEFAULT_TYPES[m])
    
    mode.change(update_types, inputs=mode, outputs=req_type)
    
    def set_fy():
        return get_fy_start(), get_today()
    
    def set_today_only():
        return "", get_today()
    
    btn_fy.click(set_fy, outputs=[date_start, date_end])
    btn_today.click(set_today_only, outputs=[date_start, date_end])
    
    def do_fetch(src, m, rt, n, de, ds, f):
        base = API_ENDPOINTS.get(src, src)
        filename = build_filename(m, rt, n, de, ds)
        
        yield {
            conn_status: "🟡 Fetching...",
            status: f"Fetching {filename}...",
            html_out: "<div style='text-align:center;padding:40px;'>🔄 Loading...</div>",
            raw_out: "",
            table_out: pd.DataFrame()
        }
        
        result = fetch_from_api(base, filename, f)
        
        if result["success"]:
            tables = extract_tables(result["content"])
            yield {
                conn_status: "🟢 Online",
                status: result["status"],
                html_out: result["content"],
                raw_out: result["content"],
                table_out: tables
            }
        else:
            yield {
                conn_status: "🔴 Error",
                status: result["status"],
                html_out: result["content"],
                raw_out: result["content"],
                table_out: pd.DataFrame({"Error": [result["status"]]})
            }
    
    btn_fetch.click(
        do_fetch,
        inputs=[api_source, mode, req_type, name, date_end, date_start, force],
        outputs=[conn_status, status, html_out, raw_out, table_out]
    )
    
    def clear():
        return {
            status: "Ready",
            html_out: "<div style='text-align:center;padding:40px;color:#9ca3af;'><div style='font-size:48px;'>📈</div><p>Ready...</p></div>",
            raw_out: "",
            table_out: pd.DataFrame(),
            conn_status: "Ready"
        }
    
    btn_clear.click(clear, outputs=[status, html_out, raw_out, table_out, conn_status])
    
    # Presets
    p1.click(lambda: ("stock", "info", "ITC", "", ""), outputs=[mode, req_type, name, date_end, date_start])
    p2.click(lambda: ("stock", "info", "RELIANCE", "", ""), outputs=[mode, req_type, name, date_end, date_start])
    p3.click(lambda: ("index", "indices", "NIFTY 50", "", ""), outputs=[mode, req_type, name, date_end, date_start])
    p4.click(lambda: ("index", "fno", "", get_today(), ""), outputs=[mode, req_type, name, date_end, date_start])
    p5.click(lambda: ("index", "fiidii", "", "", ""), outputs=[mode, req_type, name, date_end, date_start])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Local only
        show_error=True
    )