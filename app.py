from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

import stock
import indices_html
import index_live_html
import preopen_html
import eq_html
import bhavcopy_html
import nsepython
import yahooinfo
import build_nse_fno

app = FastAPI(title="Stock Backend")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Model ----------
class FetchRequest(BaseModel):
    req_type: str            # From STOCK_REQ or INDEX_REQ
    name: str
    date_start: str          # dd-mm-yyyy
    date_end: str            # dd-mm-yyyy

# ---------- STOCK Handlers ----------
def stock_info(req: FetchRequest):
    return common.wrap(yahooinfo.fetch_info(req.name))

def stock_intraday(req: FetchRequest):
    return common.wrap(stock.fetch_intraday(req.name, req.date_start, req.date_end))

def stock_daily(req: FetchRequest):
    return common.wrap(stock.fetch_daily(req.name, req.date_start, req.date_end))

def stock_nse_eq(req: FetchRequest):
    return eq_html.build_eq_html(req.name)

def stock_qresult(req: FetchRequest):
    return common.wrap(stock.fetch_qresult(req.name))

def stock_result(req: FetchRequest):
    return common.wrap(stock.fetch_result(req.name))

def stock_balance(req: FetchRequest):
    return common.wrap(stock.fetch_balance(req.name))

def stock_cashflow(req: FetchRequest):
    return common.wrap(stock.fetch_cashflow(req.name))

def stock_dividend(req: FetchRequest):
    return common.wrap(stock.fetch_dividend(req.name))

def stock_split(req: FetchRequest):
    return common.wrap(stock.fetch_split(req.name))

def stock_other(req: FetchRequest):
    return common.wrap(stock.fetch_other(req.name))

def stock_hist(req: FetchRequest):
    return nsepython.nse_stock_hist(req.date_start, req.date_end, req.name).to_html()


# ---------- INDEX Handlers ----------
def index_indices(req: FetchRequest):
    return indices_html.build_indices_html()

def index_nse_open(req: FetchRequest):
    return index_live_html.build_index_live_html()

def index_nse_preopen(req: FetchRequest):
    return preopen_html.build_preopen_html()

def index_nse_fno(req: FetchRequest):
    return build_nse_fno.nse_fno_html(req.date_end, req.name)

def index_nse_fiidii(req: FetchRequest):
    return nsepython.nse_fiidii().to_html()

def index_nse_events(req: FetchRequest):
    return nsepython.nse_events().to_html()

def index_nse_future(req: FetchRequest):
    return common.wrap(nsepython.nse_future(req.name))

def index_nse_bhav(req: FetchRequest):
    return bhavcopy_html.build_bhavcopy_html(req.date_end)

def index_nse_highlow(req: FetchRequest):
    return nsepython.nse_highlow(req.date_end).to_html()

def index_stock_highlow(req: FetchRequest):
    return nsepython.stock_highlow(req.date_end).to_html()

def index_history(req: FetchRequest):
    return nsepython.index_history("NIFTY", req.date_start, req.date_end).to_html()

def index_nse_largedeals(req: FetchRequest):
    return nsepython.nse_largedeals().to_html()

def index_nse_most_active(req: FetchRequest):
    return nsepython.nse_most_active().to_html()

def index_largedeals_historical(req: FetchRequest):
    return nsepython.nse_largedeals_historical(req.date_start, req.date_end).to_html()

def index_nse_bulkdeals(req: FetchRequest):
    return nsepython.nse_bulkdeals().to_html()

def index_nse_blockdeals(req: FetchRequest):
    return nsepython.nse_blockdeals().to_html()

def index_pe_pb_div(req: FetchRequest):
    return nsepython.index_pe_pb_div("NIFTY", req.date_start, req.date_end).to_html()

def index_total_returns(req: FetchRequest):
    return nsepython.index_total_returns("NIFTY", req.date_start, req.date_end).to_html()


# ---------- ROUTER MAPPING ----------
ROUTER = {
    # STOCK
    "info": stock_info,
    "intraday": stock_intraday,
    "daily": stock_daily,
    "nse_eq": stock_nse_eq,
    "qresult": stock_qresult,
    "result": stock_result,
    "balance": stock_balance,
    "cashflow": stock_cashflow,
    "dividend": stock_dividend,
    "split": stock_split,
    "other": stock_other,
    "stock_hist": stock_hist,

    # INDEX
    "indices": index_indices,
    "nse_open": index_nse_open,
    "nse_preopen": index_nse_preopen,
    "nse_fno": index_nse_fno,
    "nse_fiidii": index_nse_fiidii,
    "nse_events": index_nse_events,
    "nse_future": index_nse_future,
    "nse_bhav": index_nse_bhav,
    "nse_highlow": index_nse_highlow,
    "stock_highlow": index_stock_highlow,
    "index_history": index_history,
    "nse_largedeals": index_nse_largedeals,
    "nse_most_active": index_nse_most_active,
    "largedeals_historical": index_largedeals_historical,
    "nse_bulkdeals": index_nse_bulkdeals,
    "nse_blockdeals": index_nse_blockdeals,
    "index_pe_pb_div": index_pe_pb_div,
    "index_total_returns": index_total_returns
}

# ---------- MAIN ENDPOINT ----------
@app.post("/api/fetch")
def fetch_data(req: FetchRequest):
    handler = ROUTER.get(req.req_type)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unsupported req_type: {req.req_type}")
    try:
        html_content = handler(req)
        return {
            "success": True,
            "req_type": req.req_type,
            "name": req.name,
            "date_start": req.date_start,
            "date_end": req.date_end,
            "html": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
