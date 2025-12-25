import gradio as gr
import pandas as pd
import datetime

import common
import stock
import indices_html
import index_live_html
import preopen_html
import eq_html
import bhavcopy_html
import nsepython
import yahooinfo
import build_nse_fno
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Callable, Dict

app = FastAPI(title="Stock Backend")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- REQUEST MODEL (ONLY 4 FIELDS) ----------
class FetchRequest(BaseModel):
    req_type: str              # stock_info | stock_intraday | stock_daily | ...
    name: str
    date_end: str              # dd-mm-yyyy (ALWAYS REQUIRED)
    date_start: Optional[str] = None  # dd-mm-yyyy (optional)

# ---------- HEALTH ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# ---------- HANDLERS ----------
def stock_info(req: FetchRequest):
    return {
        "success": True,
        "meta": {
            "req_type": req.req_type,
            "name": req.name,
            "as_on": req.date_end
        },
        "data": {
            "sector": "FMCG",
            "market_cap": "5.2L Cr",
            "pe": 28.4
        }
    }

def stock_intraday(req: FetchRequest):
    return {
        "success": True,
        "meta": {
            "req_type": req.req_type,
            "name": req.name,
            "as_on": req.date_end,
            "interval": "5min"
        },
        "data": [
            {"time": "09:15", "close": 412.5, "volume": 120345},
            {"time": "09:20", "close": 413.8, "volume": 98234},
            {"time": "09:25", "close": 413.5, "volume": 75621}
        ]
    }

def stock_daily(req: FetchRequest):
    return {
        "success": True,
        "meta": {
            "req_type": req.req_type,
            "name": req.name,
            "to": req.date_end
        },
        "data": [
            {"date": "23-12-2025", "close": 410.2},
            {"date": "24-12-2025", "close": 412.9},
            {"date": "25-12-2025", "close": 413.5}
        ]
    }

# ---------- ROUTER ----------
ROUTER: Dict[str, Callable[[FetchRequest], dict]] = {
    "stock_info": stock_info,
    "stock_intraday": stock_intraday,
    "stock_daily": stock_daily,
}

# ---------- MAIN ENDPOINT ----------
@app.post("/api/fetch")
def fetch_data(req: FetchRequest):

    handler = ROUTER.get(req.req_type)

    if not handler:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported req_type: {req.req_type}"
        )

    return handler(req)


# ======================================================
# Date helpers
# ======================================================
def today_str():
    return datetime.date.today().strftime("%d-%m-%Y")

import datetime

def sd_ed(d: str) -> tuple[str, str]:
    base_date = datetime.datetime.strptime(d, "%d-%m-%Y").date()

    def is_working_day(x):
        return x.weekday() < 5   # Mon–Fri

    def prev_working(x):
        while not is_working_day(x):
            x -= datetime.timedelta(days=1)
        return x

    # -------- Last working day (before given date) --------
    last_working = prev_working(base_date - datetime.timedelta(days=1))

    # -------- 364-day back, fallback to 363, 362, ... --------
    past_working = prev_working(base_date - datetime.timedelta(days=364))

    return (
     
        past_working.strftime("%d-%m-%Y"),
           last_working.strftime("%d-%m-%Y")
    )


# ======================================================
# Request Type Options
# ======================================================
STOCK_REQ = [
    "info", "intraday", "daily", "nse_eq", "qresult", "result",
    "balance", "cashflow", "dividend", "split", "other", "stock_hist"
]

INDEX_REQ = [
    "indices", "nse_open", "nse_preopen", "nse_fno", "nse_fiidii",
    "nse_events", "nse_future", "nse_bhav", "nse_highlow","stock_highlow",
    "index_history", "nse_largedeals", "nse_most_active",
    "largedeals_historical", "nse_bulkdeals", "nse_blockdeals",
    "index_pe_pb_div", "index_total_returns"
]


# ======================================================
# Update UI based on mode
# ======================================================
def update_on_mode(mode):
    if mode == "stock":
        return (
            gr.update(choices=STOCK_REQ, value="info"),
            gr.update(value="ITC"),
            gr.update(value=today_str())
        )
    elif mode == "index":
        return (
            gr.update(choices=INDEX_REQ, value="indices"),
            gr.update(value="NIFTY 50"),
            gr.update(value=today_str())
        )
    return (
        gr.update(choices=[], value=""),
        gr.update(value=""),
        gr.update(value="")
    )


# ======================================================
# Data Fetcher
# ======================================================
def fetch_data(mode, req_type, name, date_str):
    req_type = req_type.lower()
    name = name.strip()
    from_date,to_date = sd_ed(date_str.strip())
   

    if mode == "index":
        if req_type == "indices":
            return indices_html.build_indices_html()
        elif req_type == "nse_open":
            return index_live_html.build_index_live_html()
        elif req_type == "nse_preopen":
            return preopen_html.build_preopen_html()
        elif req_type == "nse_fno":
            return build_nse_fno.nse_fno_html(to_date, name)
        elif req_type == "nse_events":
            return nsepython.nse_events().to_html()
        elif req_type == "nse_fiidii":
            return nsepython.nse_fiidii().to_html()
        elif req_type == "nse_future":
            return common.wrap(nsepython.nse_future(name))
        elif req_type == "nse_highlow":
            return nsepython.nse_highlow(to_date).to_html()
        elif req_type == "stock_highlow":
            return nsepython.stock_highlow(to_date).to_html()
        elif req_type == "nse_bhav":
            return bhavcopy_html.build_bhavcopy_html(to_date)
        elif req_type == "nse_largedeals":
            return nsepython.nse_largedeals().to_html()
        elif req_type == "nse_bulkdeals":
            return nsepython.nse_bulkdeals().to_html()
        elif req_type == "nse_blockdeals":
            return nsepython.nse_blockdeals().to_html()
        elif req_type == "nse_most_active":
            return nsepython.nse_most_active().to_html()
        elif req_type == "index_history":
            return nsepython.index_history("NIFTY", from_date, to_date).to_html()
        elif req_type == "largedeals_historical":
            return nsepython.nse_largedeals_historical(from_date, to_date).to_html()
        elif req_type == "index_pe_pb_div":
            return nsepython.index_pe_pb_div("NIFTY", from_date, to_date).to_html()
        elif req_type == "index_total_returns":
            return nsepython.index_total_returns("NIFTY", from_date, to_date).to_html()
        else:
            return common.wrap(f"<h3>No handler for {req_type}</h3>")

    elif mode == "stock":
        if req_type == "daily":
            return common.wrap(stock.fetch_daily(name))
        elif req_type == "nse_eq":
            return eq_html.build_eq_html(name)
        elif req_type == "intraday":
            return common.wrap(stock.fetch_intraday(name))
        elif req_type == "info":
            return common.wrap(yahooinfo.fetch_info(name))
        elif req_type == "qresult":
            return common.wrap(stock.fetch_qresult(name))
        elif req_type == "result":
            return common.wrap(stock.fetch_result(name))
        elif req_type == "balance":
            return common.wrap(stock.fetch_balance(name))
        elif req_type == "cashflow":
            return common.wrap(stock.fetch_cashflow(name))
        elif req_type == "dividend":
            return common.wrap(stock.fetch_dividend(name))
        elif req_type == "split":
            return common.wrap(stock.fetch_split(name))
        elif req_type == "other":
            return common.wrap(stock.fetch_other(name))
        elif req_type == "stock_hist":
            return nsepython.nse_stock_hist(from_date, to_date, name).to_html()
        else:
            return common.wrap(f"<h3>No handler for {req_type}</h3>")

    return common.wrap(f"<h3>No valid mode: {mode}</h3>")


# ======================================================
# Gradio UI
# ======================================================
with gr.Blocks(title="Stock / Index App") as iface:

    gr.Markdown("### **Stock / Index Data Fetcher**")

    with gr.Row():
        mode_input = gr.Radio(
            ["stock", "index"],
            label="Mode",
            value="stock",
            scale=1
        )
        name_input = gr.Textbox(label="Symbol / Index Name", scale=2)
        req_type_input = gr.Dropdown(label="Request Type", allow_custom_value=True, scale=2)
        date_input = gr.Textbox(label="Date (DD-MM-YYYY)", placeholder="Leave empty = yesterday", scale=1)
        fetch_btn = gr.Button("Fetch", scale=1)

    output = gr.HTML(label="Output")

    # Mode change → auto defaults
    mode_input.change(
        update_on_mode,
        inputs=mode_input,
        outputs=[req_type_input, name_input, date_input]
    )

    # Initial load defaults
    iface.load(
        update_on_mode,
        inputs=mode_input,
        outputs=[req_type_input, name_input, date_input]
    )

    # Fetch
    fetch_btn.click(
        fetch_data,
        inputs=[mode_input, req_type_input, name_input, date_input],
        outputs=output
    )


# ======================================================
# Launch
# ======================================================
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
