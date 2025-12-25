from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import importlib

# ---------- Auto-import all .py files in current folder ----------
current_dir = os.path.dirname(os.path.abspath(__file__))

for file in os.listdir(current_dir):
    if file.endswith(".py") and file not in ["app.py", "__init__.py"]:
        module_name = file[:-3]  # remove '.py'
        try:
            globals()[module_name] = importlib.import_module(module_name)
            print(f"Imported module: {module_name}")
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")


app = FastAPI(title="Stock / Index Backend")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Valid req_type options ----------
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

# ---------- Request Model ----------
class FetchRequest(BaseModel):
    mode: str               # stock / index
    req_type: str
    name: str
    date_start: str         # dd-mm-yyyy
    date_end: str           # dd-mm-yyyy

# ---------- Health ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# ---------- STOCK Handlers ----------
def handle_stock(req: FetchRequest):
    if req.req_type not in STOCK_REQ:
        raise HTTPException(status_code=400, detail=f"Invalid stock req_type: {req.req_type}")

    t = req.req_type.lower()
    if t == "info": return wrap(yahooinfo.fetch_info(req.name))
    if t == "intraday": return wrap(stock.fetch_intraday(req.name, req.date_start, req.date_end))
    if t == "daily": return wrap(stock.fetch_daily(req.name, req.date_start, req.date_end))
    if t == "nse_eq": return eq_html.build_eq_html(req.name)
    if t == "qresult": return wrap(stock.fetch_qresult(req.name))
    if t == "result": return wrap(stock.fetch_result(req.name))
    if t == "balance": return wrap(stock.fetch_balance(req.name))
    if t == "cashflow": return wrap(stock.fetch_cashflow(req.name))
    if t == "dividend": return wrap(stock.fetch_dividend(req.name))
    if t == "split": return wrap(stock.fetch_split(req.name))
    if t == "other": return wrap(stock.fetch_other(req.name))
    if t == "stock_hist": return nsepython.nse_stock_hist(req.date_start, req.date_end, req.name).to_html()
    return wrap(f"<h3>No handler for stock req_type: {t}</h3>")

# ---------- INDEX Handlers ----------
def handle_index(req: FetchRequest):
    if req.req_type not in INDEX_REQ:
        raise HTTPException(status_code=400, detail=f"Invalid index req_type: {req.req_type}")

    t = req.req_type.lower()
    if t == "indices": return indices_html.build_indices_html()
    if t == "nse_open": return index_live_html.build_index_live_html()
    if t == "nse_preopen": return preopen_html.build_preopen_html()
    if t == "nse_fno": return build_nse_fno.nse_fno_html(req.date_end, req.name)
    if t == "nse_fiidii": return nsepython.nse_fiidii().to_html()
    if t == "nse_events": return nsepython.nse_events().to_html()
    if t == "nse_future": return wrap(nsepython.nse_future(req.name))
    if t == "nse_highlow": return nsepython.nse_highlow(req.date_end).to_html()
    if t == "stock_highlow": return nsepython.stock_highlow(req.date_end).to_html()
    if t == "nse_bhav": return bhavcopy_html.build_bhavcopy_html(req.date_end)
    if t == "nse_largedeals": return nsepython.nse_largedeals().to_html()
    if t == "nse_bulkdeals": return nsepython.nse_bulkdeals().to_html()
    if t == "nse_blockdeals": return nsepython.nse_blockdeals().to_html()
    if t == "nse_most_active": return nsepython.nse_most_active().to_html()
    if t == "index_history": return nsepython.index_history("NIFTY", req.date_start, req.date_end).to_html()
    if t == "largedeals_historical": return nsepython.nse_largedeals_historical(req.date_start, req.date_end).to_html()
    if t == "index_pe_pb_div": return nsepython.index_pe_pb_div("NIFTY", req.date_start, req.date_end).to_html()
    if t == "index_total_returns": return nsepython.index_total_returns("NIFTY", req.date_start, req.date_end).to_html()
    return wrap(f"<h3>No handler for index req_type: {t}</h3>")

# ---------- Main POST Endpoint ----------
@app.post("/api/fetch")
def fetch_data(req: FetchRequest):
    mode = req.mode.lower()
    if mode == "stock":
        return handle_stock(req)
    elif mode == "index":
        return handle_index(req)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {req.mode}")
