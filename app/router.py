from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import mimetypes

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
from . import daily

# -------------------------------------------------------
# Router
# -------------------------------------------------------
router = APIRouter()

# -------------------------------------------------------
# Persistent storage (HF)
# -------------------------------------------------------
FILES_DIR = Path("/data/files")
FILES_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------
# Request model (kept)
# -------------------------------------------------------
class FetchRequest(BaseModel):
    mode: str
    req_type: str
    name: str = ""
    date_start: str = ""
    date_end: str = ""

# -------------------------------------------------------
# Filename → FetchRequest
# stock_info_TCS_view.html
# index_open_NIFTY_live.html
# screener_topgainers_all_view.html
# -------------------------------------------------------
def parse_filename(filename: str) -> FetchRequest:
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("_")

    if len(parts) < 3:
        raise ValueError("Invalid filename format")

    return FetchRequest(
        mode=parts[0],
        req_type=parts[1],
        name=parts[2]
    )

# -------------------------------------------------------
# STOCK handler (UNCHANGED LOGIC)
# -------------------------------------------------------
def handle_stock(req: FetchRequest):
    t = req.req_type.lower()

    if t == "info":
        return yahooinfo.fetch_info(req.name)
    if t == "intraday":
        return stock.fetch_intraday(req.name)
    if t == "daily":
        return daily.fetch_daily(req.name, req.date_end, req.date_start)
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
        return ns.nse_stock_hist(
            req.date_start, req.date_end, req.name
        ).to_html()

    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")

# -------------------------------------------------------
# INDEX handler (UNCHANGED LOGIC)
# -------------------------------------------------------
def handle_index(req: FetchRequest):
    t = req.req_type.lower()

    if t == "indices":
        return indices.build_indices_html()
    if t == "open":
        return live.build_index_live_html(req.name)
    if t == "preopen":
        return pre.build_preopen_html(req.name)
    if t == "fno":
        return fno.nse_fno_html(req.date_end, req.name)
    if t == "fiidii":
        return ns.nse_fiidii()
    if t == "events":
        return ns.nse_events()
    if t == "index_highlow":
        return ns.nse_highlow(req.date_end)
    if t == "stock_highlow":
        return ns.stock_highlow(req.date_end)
    if t == "bhav":
        return bhav.build_bhavcopy_html(req.date_end)
    if t == "largedeals":
        return ns.nse_largedeals()
    if t == "bulkdeals":
        return ns.nse_bulkdeals()
    if t == "blockdeals":
        return ns.nse_blockdeals()
    if t == "most_active":
        return ns.nse_most_active()
    if t == "index_history":
        return ns.index_history("NIFTY", req.date_start, req.date_end)
    if t == "hlargedeals":
        return ns.nse_largedeals_historical(req.date_start, req.date_end)
    if t == "pe_pb":
        return ns.index_pe_pb_div("NIFTY", req.date_start, req.date_end)
    if t == "total_returns":
        return ns.index_total_returns("NIFTY", req.date_start, req.date_end)

    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")

# -------------------------------------------------------
# SCREENER handler
# -------------------------------------------------------
def handle_screener(req: FetchRequest):
    return screener.fetch_screener(req.req_type.lower())

# -------------------------------------------------------
# Health
# -------------------------------------------------------
@router.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}

# -------------------------------------------------------
# FILE endpoint (CORE)
# -------------------------------------------------------
@router.get("/file")
def get_file(name: str, force: bool = Query(False)):
    file_path = (FILES_DIR / name).resolve()

    # Security
    if not str(file_path).startswith(str(FILES_DIR)):
        raise HTTPException(403, "Invalid path")

    # Generate if missing
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