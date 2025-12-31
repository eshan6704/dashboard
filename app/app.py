
from .router import *
# -------------------------------------------------------
# FastAPI app
# -------------------------------------------------------
app = FastAPI(title="Stock / Index Backend")

# -------------------------------------------------------
# Middleware
# -------------------------------------------------------
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
    req_type: str
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
# Main API
# -------------------------------------------------------
@app.post("/api/fetch", response_class=HTMLResponse)
def fetch_data(req: FetchRequest):

    mode = req.mode.lower()

    # ✅ Used by frontend on page load
    if mode == "list":
        return HTMLResponse(content=router.build_req_type_list_html())

    if mode == "stock":
        html = router.handle_stock(req)

    elif mode == "index":
        html = router.handle_index(req)

    elif mode == "screener":
        html = router.handle_screener(req)

    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

    # 🔒 Always return HTML
    return HTMLResponse(content=str(html))
