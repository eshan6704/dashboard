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
# API Routes (from router)
# -------------------------------------------------------
app.include_router(router)

# -------------------------------------------------------
# Gradio UI Configuration
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
    """Call own API internally using requests"""
    try:
        # In HF Space, call localhost:7860 (same container)
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
    """Extract pandas DataFrames from HTML tables"""
    try:
        tables = pd.read_html(html_content)
        if tables:
            if len(tables) == 1:
                return tables[0]
            else:
                # Combine multiple tables
                return pd.concat(tables, ignore_index=True)
    except Exception:
        pass
    return pd.DataFrame({"Info": ["No tables found in response"]})

# -------------------------------------------------------
# Build Gradio Interface
# -------------------------------------------------------

with gr.Blocks(
    title="NSE Stock Dashboard",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue"),
    css="""
    .gradio-container { max-width: 95% !important; }
    .output-html { min-height: 600px; }
    """
) as demo:
    
    gr.Markdown("""
    # 📈 NSE Stock Dashboard
    
    **HuggingFace Space Deployment** | FastAPI Backend + Gradio Frontend
    """)
    
    # Input Panel
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            gr.Markdown("### 🔧 Configuration")
            
            mode = gr.Radio(
                label="Mode",
                choices=["stock", "index", "screener"],
                value="stock"
            )
            
            req_type = gr.Dropdown(
                label="Request Type",
                choices=REQ_TYPES["stock"],
                value="info"
            )
            
            name = gr.Textbox(
                label="Symbol / Name",
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
            
            force_refresh = gr.Checkbox(
                label="⚡ Force Refresh (ignore cache)",
                value=False
            )
            
            with gr.Row():
                btn_fetch = gr.Button("🚀 Fetch Data", variant="primary", scale=2)
                btn_clear = gr.Button("🗑️ Clear", scale=1)
            
            # Presets
            gr.Markdown("### ⚡ Quick Presets")
            with gr.Row():
                preset_itc = gr.Button("ITC", size="sm")
                preset_reliance = gr.Button("RELIANCE", size="sm")
                preset_nifty = gr.Button("NIFTY 50", size="sm")
            with gr.Row():
                preset_fno = gr.Button("F&O Today", size="sm")
                preset_fiidii = gr.Button("FII/DII", size="sm")
                preset_preopen = gr.Button("Pre-Open", size="sm")
        
        # Output Panel
        with gr.Column(scale=3):
            status_text = gr.Textbox(
                label="Status",
                value="Ready to fetch data...",
                interactive=False
            )
            
            with gr.Tabs():
                with gr.TabItem("📊 Rendered HTML"):
                    html_output = gr.HTML(
                        show_label=False,
                        min_height=600
                    )
                
                with gr.TabItem("📋 Data Table"):
                    table_output = gr.DataFrame(
                        show_label=False,
                        interactive=False,
                        height=600
                    )
                
                with gr.TabItem("📝 Raw HTML"):
                    raw_output = gr.Code(
                        language="html",
                        show_label=False,
                        min_height=600
                    )
    
    # -------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------
    
    # Update request types when mode changes
    def update_types(selected_mode):
        return gr.Dropdown(
            choices=REQ_TYPES[selected_mode],
            value=DEFAULT_TYPES[selected_mode]
        )
    
    mode.change(
        update_types,
        inputs=mode,
        outputs=req_type
    )
    
    # Date helpers
    btn_fy.click(
        lambda: (get_fy_start(), get_today()),
        outputs=[date_start, date_end]
    )
    
    btn_today.click(
        lambda: ("", get_today()),
        outputs=[date_start, date_end]
    )
    
    # Main fetch function
    def handle_fetch(m, rt, n, de, ds, force):
        filename = build_filename(m, rt, n, de, ds)
        
        # Update UI to loading state
        yield {
            status_text: f"⏳ Fetching: {filename}",
            html_output: "<div style='text-align:center; padding:50px;'><div style='font-size:48px;'>🔄</div><p>Loading data...</p></div>",
            raw_output: "",
            table_output: pd.DataFrame()
        }
        
        # Fetch data
        result = fetch_data_internal(filename, force)
        
        if result["success"]:
            content = result["content"]
            tables = extract_tables(content)
            
            yield {
                status_text: f"✅ Success | {result['size']:,} chars | {len(tables)} rows",
                html_output: content,
                raw_output: content,
                table_output: tables
            }
        else:
            error_html = f"<div style='color:red; padding:20px;'><h3>Error</h3><p>{result.get('error', 'Unknown error')}</p></div>"
            yield {
                status_text: f"❌ Error: {result.get('error', 'Unknown')}",
                html_output: error_html,
                raw_output: str(result),
                table_output: pd.DataFrame({"Error": [result.get("error", "Unknown")]})
            }
    
    btn_fetch.click(
        handle_fetch,
        inputs=[mode, req_type, name, date_end, date_start, force_refresh],
        outputs=[status_text, html_output, raw_output, table_output]
    )
    
    # Clear function
    def handle_clear():
        return {
            status_text: "Ready",
            html_output: "<div style='text-align:center; padding:50px; color:#9ca3af;'><div style='font-size:64px; margin-bottom:20px;'>📈</div><h3>NSE Stock Dashboard</h3><p>Select parameters and click Fetch Data</p></div>",
            raw_output: "",
            table_output: pd.DataFrame()
        }
    
    btn_clear.click(
        handle_clear,
        outputs=[status_text, html_output, raw_output, table_output]
    )
    
    # Presets
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

# -------------------------------------------------------
# Mount Gradio at ROOT (so HF Space shows UI immediately)
# -------------------------------------------------------
app = gr.mount_gradio_app(app, demo, path="/")

# Note: API routes from router are still accessible at their paths
# /file endpoint works for both Gradio internal calls and external API calls