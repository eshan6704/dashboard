from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import mimetypes

import mimetypes

# Absolute imports
from app.common import common
from app.nse import stock
from app.nse import indices_html as indices
from app.nse import index_live_html as live
from app.nse import preopen_html as pre
from app.nse import eq_html as eq
from app.nse import bhavcopy_html as bhav
from app.nse import build_nse_fno as fno
from app.nse import nsepythonmodified as ns

from app.yahoofinance import yahooinfo
from app.yahoofinance import screener
from app.yahoofinance import daily
router = APIRouter()

# Persistent storage
FILES_DIR = Path("/data/files")
FILES_DIR.mkdir(parents=True, exist_ok=True)

# Request model
class FetchRequest(BaseModel):
    mode: str
    req_type: str
    name: str = ""
    end_date: str = ""
    start_date: str = ""
    suffix: str = ""

# -------------------------------
# Parse filename convention
# @mode@req_type@name[@enddate@startdate@suffix].html
# -------------------------------
def parse_filename(filename: str) -> FetchRequest:
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("@")[1:]  # remove leading empty before first @

    if len(parts) < 3:
        raise ValueError("Invalid filename format, must have at least mode@req_type@name")

    mode, req_type, name = parts[0:3]
    end_date = parts[3] if len(parts) > 3 else ""
    start_date = parts[4] if len(parts) > 4 else ""
    suffix = parts[5] if len(parts) > 5 else ""

    return FetchRequest(
        mode=mode,
        req_type=req_type,
        name=name,
        end_date=end_date,
        start_date=start_date,
        suffix=suffix
    )

# -------------------------------
# Handlers remain the same
# -------------------------------
def handle_stock(req: FetchRequest):
    t = req.req_type.lower()
    if t == "info":
        return yahooinfo.fetch_info(req.name)
    if t == "intraday":
        return stock.fetch_intraday(req.name)
    if t == "daily":
        return daily.fetch_daily(req.name, req.end_date, req.start_date)
    if t == "nse_eq":
        return eq.build_eq_html(req.name)
    if t == "qresult":
        return stock.fetch_qresult(req.name)
    if t == "result":
        return stock.fetch_result(req.name)
    if t == "balance":
        return stock.fetch_balance(req.name)
    if t == "cashflow":
        return stock.fetch_cashflow(req.name)
    if t == "dividend":
        return stock.fetch_dividend(req.name)
    if t == "split":
        return stock.fetch_split(req.name)
    if t == "other":
        return stock.fetch_other(req.name)
    if t == "stock_hist":
        return ns.nse_stock_hist(req.start_date, req.end_date, req.name).to_html()
    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")

def handle_index(req: FetchRequest):
    t = req.req_type.lower()
    if t == "indices":
        return indices.build_indices_html()
    if t == "open":
        return live.build_index_live_html(req.name)
    if t == "preopen":
        return pre.build_preopen_html(req.name)
    if t == "fno":
        return fno.nse_fno_html(req.end_date, req.name)
    if t == "fiidii":
        return ns.nse_fiidii()
    if t == "events":
        return ns.nse_events()
    if t == "index_highlow":
        return ns.nse_highlow(req.end_date)
    if t == "stock_highlow":
        return ns.stock_highlow(req.end_date)
    if t == "bhav":
        return bhav.build_bhavcopy_html(req.end_date)
    if t == "largedeals":
        return ns.nse_largedeals()
    if t == "bulkdeals":
        return ns.nse_bulkdeals()
    if t == "blockdeals":
        return ns.nse_blockdeals()
    if t == "most_active":
        return ns.nse_most_active()
    if t == "index_history":
        return ns.index_history("NIFTY", req.start_date, req.end_date)
    if t == "hlargedeals":
        return ns.nse_largedeals_historical(req.start_date, req.end_date)
    if t == "pe_pb":
        return ns.index_pe_pb_div("NIFTY", req.start_date, req.end_date)
    if t == "total_returns":
        return ns.index_total_returns("NIFTY", req.start_date, req.end_date)
    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")

def handle_screener(req: FetchRequest):
    return screener.fetch_screener(req.req_type.lower())

# -------------------------------
# Health
# -------------------------------
@router.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# -------------------------------
# FILE endpoint
# -------------------------------
@router.get("/file")
def get_file(name: str, force: bool = Query(False)):
    file_path = (FILES_DIR / name).resolve()

    if not str(file_path).startswith(str(FILES_DIR)):
        raise HTTPException(403, "Invalid path")

    if force or not file_path.exists():
        try:
            req = parse_filename(name)
        except Exception:
            raise HTTPException(400, "Invalid filename")

        if req.mode == "stock":
            html = handle_stock(req)
        elif req.mode == "index":
            html = handle_index(req)
        elif req.mode == "screener":
            html = handle_screener(req)
        else:
            raise HTTPException(400, "Invalid mode")

        file_path.write_text(str(html), encoding="utf-8")

    if not file_path.exists():
        raise HTTPException(404, "File not found")

    media_type, _ = mimetypes.guess_type(file_path)

    return FileResponse(
        file_path,
        media_type=media_type or "application/octet-stream",
        filename=file_path.name,
        headers={"Content-Disposition": f'inline; filename="{file_path.name}"'}
    )