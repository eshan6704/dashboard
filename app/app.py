from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

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
from . import ui_html   # ✅ NEW

app = FastAPI(title="Stock / Index Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

class FetchRequest(BaseModel):
    mode: str
    req_type: str = ""
    name: str = ""
    date_start: str = ""
    date_end: str = ""

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/ui", response_class=HTMLResponse)
def frontend():
    return ui_html.build_frontend_html()

REQ_TYPE_MAP = {
    "stock": ["info","intraday","daily","nse_eq","qresult","result","balance",
              "cashflow","dividend","split","other","stock_hist","nse_bhav"],
    "index": ["indices","nse_open","nse_preopen","nse_fno","nse_fiidii",
              "nse_events","nse_future","nse_highlow","stock_highlow",
              "nse_largedeals","nse_bulkdeals","nse_blockdeals",
              "nse_most_active","index_history","largedeals_historical",
              "index_pe_pb_div","index_total_returns"]
}

FNO_STOCK_LIST = ["ITC","ZEEL","PNB","NIFTY"]
OPEN_INDICES_LIST = ["NIFTY 50","NIFTY BANK"]
PREOPEN_INDICES_LIST = ["NIFTY 50","NIFTY BANK"]

def build_req_type_list_html():
    h = ["<div>"]

    h.append("<h3>STOCK</h3><ul>")
    for t in REQ_TYPE_MAP["stock"]:
        names = ",".join(FNO_STOCK_LIST) if t in ["stock_hist","nse_bhav"] else ""
        h.append(f"<li data-mode='stock' data-type='{t}' data-names='{names}'>{t}</li>")
    h.append("</ul>")

    h.append("<h3>INDEX</h3><ul>")
    for t in REQ_TYPE_MAP["index"]:
        if t == "nse_open":
            names = ",".join(OPEN_INDICES_LIST)
        elif t == "nse_preopen":
            names = ",".join(PREOPEN_INDICES_LIST)
        else:
            names = ""
        h.append(f"<li data-mode='index' data-type='{t}' data-names='{names}'>{t}</li>")
    h.append("</ul>")

    h.append("<h3>SCREENER</h3><ul>")
    for k in screener.SCREENER_MAP:
        h.append(f"<li data-mode='screener' data-type='{k}'>{k}</li>")
    h.append("</ul></div>")

    return "".join(h)

@app.post("/api/fetch", response_class=HTMLResponse)
def fetch(req: FetchRequest):
    if req.mode == "list":
        return build_req_type_list_html()

    if req.mode == "stock":
        return HTMLResponse(str(stock.fetch_intraday(req.name))) if req.req_type=="intraday" else yahooinfo.fetch_info(req.name)

    if req.mode == "index":
        return indices.build_indices_html()

    if req.mode == "screener":
        return screener.fetch_screener(req.req_type)

    raise HTTPException(400, "Invalid mode")
