from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# -------------------------------------------------------
# Router
# -------------------------------------------------------
from .router import router   # ← same import style

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

# Enable gzip compression for large HTML files
app.add_middleware(GZipMiddleware, minimum_size=1000)

# -------------------------------------------------------
# Routes
# -------------------------------------------------------
app.include_router(router)