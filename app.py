import os
import importlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Callable

# ---------- Dynamically import all .py files ----------
current_dir = os.path.dirname(os.path.abspath(__file__))
modules = {}
for file in os.listdir(current_dir):
    if file.endswith(".py") and file != "app.py":
        name = file[:-3]
        try:
            modules[name] = importlib.import_module(name)
            print(f"Imported module: {name}")
        except Exception as e:
            print(f"Failed importing {name}: {e}")

# ---------- FastAPI ----------
app = FastAPI(title="Stock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Model ----------
class FetchRequest(BaseModel):
    req_type: str           # like 'info', 'intraday', 'nse_open', etc.
    mode: str               # 'stock' or 'index'
    name: str               # symbol or index name
    date_start: str         # dd-mm-yyyy
    date_end: str           # dd-mm-yyyy

# ---------- Health Check ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# ---------- STOCK & INDEX Request Mapping ----------
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

# ---------- Handler Router ----------
ROUTER: Dict[str, Callable[[FetchRequest], str]] = {}

# STOCK ROUTES
if 'stock' in modules:
    ROUTER.update({
        "info": lambda r: modules['yahooinfo'].fetch_info(r.name),
        "intraday": lambda r: modules['stock'].fetch_intraday(r.name, r.date_start, r.date_end),
        "daily": lambda r: modules['stock'].fetch_daily(r.name, r.date_start, r.date_end),
        "nse_eq": lambda r: modules['eq_html'].build_eq_html(r.name),
        "qresult": lambda r: modules['stock'].fetch_qresult(r.name),
        "result": lambda r: modules['stock'].fetch_result(r.name),
        "balance": lambda r: modules['stock'].fetch_balance(r.name),
        "cashflow": lambda r: modules['stock'].fetch_cashflow(r.name),
        "dividend": lambda r: modules['stock'].fetch_dividend(r.name),
        "split": lambda r: modules['stock'].fetch_split(r.name),
        "other": lambda r: modules['stock'].fetch_other(r.name),
    })

if 'nsepython' in modules:
    ROUTER["stock_hist"] = lambda r: modules['nsepython'].nse_stock_hist(r.date_start, r.date_end, r.name).to_html()

# INDEX ROUTES
if 'indices_html' in modules:
    ROUTER["indices"] = lambda r: modules['indices_html'].build_indices_html()
if 'index_live_html' in modules:
    ROUTER["nse_open"] = lambda r: modules['index_live_html'].build_index_live_html()
if 'preopen_html' in modules:
    ROUTER["nse_preopen"] = lambda r: modules['preopen_html'].build_preopen_html()
if 'build_nse_fno' in modules:
    ROUTER["nse_fno"] = lambda r: modules['build_nse_fno'].nse_fno_html(r.date_end, r.name)
if 'nsepython' in modules:
    ROUTER.update({
        "nse_events": lambda r: modules['nsepython'].nse_events().to_html(),
        "nse_fiidii": lambda r: modules['nsepython'].nse_fiidii().to_html(),
        "nse_future": lambda r: modules['nsepython'].nse_future(r.name),
        "nse_highlow": lambda r: modules['nsepython'].nse_highlow(r.date_end).to_html(),
        "stock_highlow": lambda r: modules['nsepython'].stock_highlow(r.date_end).to_html(),
        "index_history": lambda r: modules['nsepython'].index_history(r.name, r.date_start, r.date_end).to_html(),
        "largedeals_historical": lambda r: modules['nsepython'].nse_largedeals_historical(r.date_start, r.date_end).to_html(),
        "index_pe_pb_div": lambda r: modules['nsepython'].index_pe_pb_div(r.name, r.date_start, r.date_end).to_html(),
        "index_total_returns": lambda r: modules['nsepython'].index_total_returns(r.name, r.date_start, r.date_end).to_html(),
    })
if 'bhavcopy_html' in modules:
    ROUTER["nse_bhav"] = lambda r: modules['bhavcopy_html'].build_bhavcopy_html(r.date_end)

# ---------- Fetch Endpoint ----------
@app.post("/api/fetch")
def fetch_data(req: FetchRequest):
    handler = ROUTER.get(req.req_type)
    if not handler:
        raise HTTPException(status_code=400, detail=f"No handler for req_type: {req.req_type}")

    try:
        result = handler(req)
        if 'common' in modules and hasattr(modules['common'], 'wrap'):
            return modules['common'].wrap(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
