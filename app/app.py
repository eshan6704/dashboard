from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

# -------------------------------------------------------
# Local modules (UNCHANGED)
# -------------------------------------------------------
from . import common
from . import stock
from . import indices_html as indices
from . import index_live_html as live
from . import preopen_html as pre
from . import eq_html as eq
from . import bhavcopy_html as bhav
from . import build_nse_fno as fno
from . import nsepythonmodified as ns
from . import yahooinfo
from . import screener
from . import ui_html   # ✅ ONLY HTML, no logic

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
app.add_middleware(GZipMiddleware, minimum_size=1000)

# -------------------------------------------------------
# Request model
# -------------------------------------------------------
class FetchRequest(BaseModel):
    mode: str
    req_type: str = ""
    name: str = ""
    date_start: str = ""
    date_end: str = ""

# -------------------------------------------------------
# Health
# -------------------------------------------------------
@app.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# -------------------------------------------------------
# CONFIG (single source of truth)
# -------------------------------------------------------
REQ_TYPE_MAP = {
    "stock": [
        "info","intraday","daily","nse_eq","qresult",
        "result","balance","cashflow","dividend",
        "split","other","stock_hist","nse_bhav"
    ],
    "index": [
        "indices","nse_open","nse_preopen","nse_fno",
        "nse_fiidii","nse_events","nse_future",
        "nse_highlow","stock_highlow","nse_largedeals",
        "nse_bulkdeals","nse_blockdeals","nse_most_active",
        "index_history","largedeals_historical",
        "index_pe_pb_div","index_total_returns"
    ],
}

# -------------------------------------------------------
# Name lists (backend authority)
# -------------------------------------------------------
FNO_STOCK_LIST = ["ITC","ZEEL","PNB","NIFTY"]
OPEN_INDICES_LIST = ["NIFTY 50","NIFTY BANK"]
PREOPEN_INDICES_LIST = ["NIFTY 50","NIFTY BANK"]

# -------------------------------------------------------
# 🔹 LIST BUILDER (frontend bootstrap)
# -------------------------------------------------------
def build_req_type_list_html():
    html = ["<div id='backend_meta'>"]

    # STOCK
    for t in REQ_TYPE_MAP["stock"]:
        names = ",".join(FNO_STOCK_LIST) if t in ["stock_hist","nse_bhav"] else ""
        html.append(
            f"<li data-mode='stock' data-type='{t}' data-names='{names}'></li>"
        )

    # INDEX
    for t in REQ_TYPE_MAP["index"]:
        if t == "nse_open":
            names = ",".join(OPEN_INDICES_LIST)
        elif t == "nse_preopen":
            names = ",".join(PREOPEN_INDICES_LIST)
        else:
            names = ""
        html.append(
            f"<li data-mode='index' data-type='{t}' data-names='{names}'></li>"
        )

    # SCREENER
    for key in screener.SCREENER_MAP:
        html.append(
            f"<li data-mode='screener' data-type='{key}'></li>"
        )

    html.append("</div>")
    return "".join(html)

# -------------------------------------------------------
# UI (HTML only)
# -------------------------------------------------------
@app.get("/ui", response_class=HTMLResponse)
def ui():
    return ui_html.HTML

# -------------------------------------------------------
# HANDLERS (ALL preserved)
# -------------------------------------------------------
def handle_stock(req: FetchRequest):
    t = req.req_type.lower()
    if t == "info": return yahooinfo.fetch_info(req.name)
    if t == "intraday": return stock.fetch_intraday(req.name)
    if t == "daily": return stock.fetch_daily(req.name, req.date_end)
    if t == "nse_eq": return eq.build_eq_html(req.name)
    if t == "qresult": return stock.fetch_qresult(req.name)
    if t == "result": return stock.fetch_result(req.name)
    if t == "balance": return stock.fetch_balance(req.name)
    if t == "cashflow": return stock.fetch_cashflow(req.name)
    if t == "dividend": return stock.fetch_dividend(req.name)
    if t == "split": return stock.fetch_split(req.name)
    if t == "other": return stock.fetch_other(req.name)
    if t in ["stock_hist","nse_bhav"]:
        return ns.nse_stock_hist(req.date_start, req.date_end, req.name).to_html()
    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")

def handle_index(req: FetchRequest):
    t = req.req_type.lower()
    if t == "indices": return indices.build_indices_html()
    if t == "nse_open": return live.build_index_live_html()
    if t == "nse_preopen": return pre.build_preopen_html()
    if t == "nse_fno": return fno.nse_fno_html(req.date_end, req.name)
    if t == "nse_fiidii": return ns.nse_fiidii()
    if t == "nse_events": return ns.nse_events()
    if t == "nse_future": return ns.nse_future(req.name)
    if t == "nse_highlow": return ns.nse_highlow(req.date_end)
    if t == "stock_highlow": return ns.stock_highlow(req.date_end)
    if t == "nse_largedeals": return ns.nse_largedeals()
    if t == "nse_bulkdeals": return ns.nse_bulkdeals()
    if t == "nse_blockdeals": return ns.nse_blockdeals()
    if t == "nse_most_active": return ns.nse_most_active()
    if t == "index_history":
        return ns.index_history("NIFTY", req.date_start, req.date_end)
    if t == "largedeals_historical":
        return ns.nse_largedeals_historical(req.date_start, req.date_end)
    if t == "index_pe_pb_div":
        return ns.index_pe_pb_div("NIFTY", req.date_start, req.date_end)
    if t == "index_total_returns":
        return ns.index_total_returns("NIFTY", req.date_start, req.date_end)
    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")

def handle_screener(req: FetchRequest):
    return screener.fetch_screener(req.req_type.lower())

# -------------------------------------------------------
# MAIN API
# -------------------------------------------------------
@app.post("/api/fetch", response_class=HTMLResponse)
def fetch_data(req: FetchRequest):

    # 🔑 Frontend bootstrap
    if req.mode == "list":
        return build_req_type_list_html()

    if req.mode == "stock":
        html = handle_stock(req)
    elif req.mode == "index":
        html = handle_index(req)
    elif req.mode == "screener":
        html = handle_screener(req)
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

    return HTMLResponse(content=str(html))
