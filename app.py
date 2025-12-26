from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import importlib.util

# -------------------------------------------------------
# Explicit module loader (HF-safe)
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name):
    path = os.path.join(BASE_DIR, f"{name}.py")
    if not os.path.exists(path):
        raise ImportError(f"Module file not found: {path}")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# -------------------------------------------------------
# Load ALL local modules explicitly
# -------------------------------------------------------
common = load_module("common")
stock = load_module("stock")
indices_html = load_module("indices_html")
index_live_html = load_module("index_live_html")
preopen_html = load_module("preopen_html")
eq_html = load_module("eq_html")
bhavcopy_html = load_module("bhavcopy_html")
build_nse_fno = load_module("build_nse_fno")

# External libs (installed via requirements.txt)
import nsepython
import yahooinfo

# -------------------------------------------------------
# FastAPI app
# -------------------------------------------------------
app = FastAPI(title="Stock / Index Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Valid request types
# -------------------------------------------------------
STOCK_REQ = [
    "info", "intraday", "daily", "nse_eq", "qresult", "result",
    "balance", "cashflow", "dividend", "split", "other", "stock_hist"
]

INDEX_REQ = [
    "indices", "nse_open", "nse_preopen", "nse_fno", "nse_fiidii",
    "nse_events", "nse_future", "nse_bhav", "nse_highlow", "stock_highlow",
    "index_history", "nse_largedeals", "nse_most_active",
    "largedeals_historical", "nse_bulkdeals", "nse_blockdeals",
    "index_pe_pb_div", "index_total_returns"
]

# -------------------------------------------------------
# Request model
# -------------------------------------------------------
class FetchRequest(BaseModel):
    mode: str
    req_type: str
    name: str
    date_start: str
    date_end: str

# -------------------------------------------------------
# Health
# -------------------------------------------------------
@app.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# -------------------------------------------------------
# STOCK handler
# -------------------------------------------------------
def handle_stock(req: FetchRequest):
    t = req.req_type.lower()

    if t == "info":
        return common.wrap(yahooinfo.fetch_info(req.name))
    if t == "intraday":
        return common.wrap(stock.fetch_intraday(req.name, req.date_start, req.date_end))
    if t == "daily":
        return common.wrap(stock.fetch_daily(req.name, req.date_start, req.date_end))
    if t == "nse_eq":
        return eq_html.build_eq_html(req.name)
    if t == "qresult":
        return common.wrap(stock.fetch_qresult(req.name))
    if t == "result":
        return common.wrap(stock.fetch_result(req.name))
    if t == "balance":
        return common.wrap(stock.fetch_balance(req.name))
    if t == "cashflow":
        return common.wrap(stock.fetch_cashflow(req.name))
    if t == "dividend":
        return common.wrap(stock.fetch_dividend(req.name))
    if t == "split":
        return common.wrap(stock.fetch_split(req.name))
    if t == "other":
        return common.wrap(stock.fetch_other(req.name))
    if t == "stock_hist":
        return nsepython.nse_stock_hist(
            req.date_start, req.date_end, req.name
        ).to_html()

    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")

# -------------------------------------------------------
# INDEX handler
# -------------------------------------------------------
def handle_index(req: FetchRequest):
    t = req.req_type.lower()

    if t == "indices":
        return indices_html.build_indices_html()
    if t == "nse_open":
        return index_live_html.build_index_live_html()
    if t == "nse_preopen":
        return preopen_html.build_preopen_html()
    if t == "nse_fno":
        return build_nse_fno.nse_fno_html(req.date_end, req.name)
    if t == "nse_fiidii":
        return nsepython.nse_fiidii().to_html()
    if t == "nse_events":
        return nsepython.nse_events().to_html()
    if t == "nse_future":
        return common.wrap(nsepython.nse_future(req.name))
    if t == "nse_highlow":
        return nsepython.nse_highlow(req.date_end).to_html()
    if t == "stock_highlow":
        return nsepython.stock_highlow(req.date_end).to_html()
    if t == "nse_bhav":
        return bhavcopy_html.build_bhavcopy_html(req.date_end)
    if t == "nse_largedeals":
        return nsepython.nse_largedeals().to_html()
    if t == "nse_bulkdeals":
        return nsepython.nse_bulkdeals().to_html()
    if t == "nse_blockdeals":
        return nsepython.nse_blockdeals().to_html()
    if t == "nse_most_active":
        return nsepython.nse_most_active().to_html()
    if t == "index_history":
        return nsepython.index_history("NIFTY", req.date_start, req.date_end).to_html()
    if t == "largedeals_historical":
        return nsepython.nse_largedeals_historical(
            req.date_start, req.date_end
        ).to_html()
    if t == "index_pe_pb_div":
        return nsepython.index_pe_pb_div(
            "NIFTY", req.date_start, req.date_end
        ).to_html()
    if t == "index_total_returns":
        return nsepython.index_total_returns(
            "NIFTY", req.date_start, req.date_end
        ).to_html()

    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")

# -------------------------------------------------------
# Main API
# -------------------------------------------------------
@app.post("/api/fetch")
def fetch_data(req: FetchRequest):
    if req.mode.lower() == "stock":
        return handle_stock(req)
    if req.mode.lower() == "index":
        return handle_index(req)

    raise HTTPException(status_code=400, detail="Invalid mode")