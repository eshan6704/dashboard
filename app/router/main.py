from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.persist import exists, load, save
from .parser import parse_filename
from .handlers import handle_stock, handle_index, handle_screener

router = APIRouter()

# -------------------------------
# Health check
# -------------------------------
@router.get("/")
def health():
    return {"status": "ok", "service": "backend alive"}


# -------------------------------
# File endpoint (cache-first)
# -------------------------------
@router.get("/file")
def get_file(name: str, force: bool = Query(False)):
    if not name.endswith(".html"):
        raise HTTPException(400, "Only .html supported")

    base_name = name.rsplit(".", 1)[0]

    # -------------------------------
    # 1️⃣ Serve from cache
    # -------------------------------
    if not force and exists(base_name, "html"):
        html = load(base_name, "html")
        if html:
            return HTMLResponse(content=html)

    # -------------------------------
    # 2️⃣ Generate HTML
    # -------------------------------
    try:
        req = parse_filename(name)
    except Exception:
        raise HTTPException(400, "Invalid filename format")

    if req.mode == "stock":
        html = handle_stock(req)
    elif req.mode == "index":
        html = handle_index(req)
    elif req.mode == "screener":
        html = handle_screener(req)
    else:
        raise HTTPException(400, "Invalid mode")

    # -------------------------------
    # 3️⃣ Persist & return
    # -------------------------------
    save(base_name, html, "html")
    return HTMLResponse(content=str(html))
