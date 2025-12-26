from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import importlib.util

# -------------------------------------------------------
# 
# -------------------------------------------------------
# Load ALL local modules explicitly
# -------------------------------------------------------
from . import common
from . import stock
from . import indices_html
from . import index_live_html
from . import preopen_html
from . import eq_html
from . import bhavcopy_html
from . import build_nse_fno
from . import nsepythonmodified

# External libs (installed via requirements.txt)
#import nsepython as nse
from . import yahooinfo

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
        return nsepythonmodied.nse_stock_hist(
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
        return nsepythonmodied.nse_fiidii().to_html()
    if t == "nse_events":
        return nsepythonmodied.nse_events().to_html()
    if t == "nse_future":
        return common.wrap(nsepython.nse_future(req.name))
    if t == "nse_highlow":
        return nsepythonmodied.nse_highlow(req.date_end).to_html()
    if t == "stock_highlow":
        return nsepythonmodied.stock_highlow(req.date_end).to_html()
    if t == "nse_bhav":
        return bhavcopy_html.build_bhavcopy_html(req.date_end)
    if t == "nse_largedeals":
        return nsepythonmodied.nse_largedeals().to_html()
    if t == "nse_bulkdeals":
        return nsepythonmodied.nse_bulkdeals().to_html()
    if t == "nse_blockdeals":
        return nsepythonmodied.nse_blockdeals().to_html()
    if t == "nse_most_active":
        return nsepython.nse_most_active().to_html()
    if t == "index_history":
        return nsepythonmodied.index_history("NIFTY", req.date_start, req.date_end).to_html()
    if t == "largedeals_historical":
        return nsepythonmodied.nse_largedeals_historical(
            req.date_start, req.date_end
        ).to_html()
    if t == "index_pe_pb_div":
        return nsepythonmodied.index_pe_pb_div(
            "NIFTY", req.date_start, req.date_end
        ).to_html()
    if t == "index_total_returns":
        return nsepythonmodied.index_total_returns(
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