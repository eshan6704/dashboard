from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import gradio as gr

from app.router.router import router
from app.gradio_ui import create_interface

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
# API Routes
# -------------------------------------------------------
app.include_router(router)

# -------------------------------------------------------
# Gradio UI
# -------------------------------------------------------
demo = create_interface()
app = gr.mount_gradio_app(app, demo, path="/")