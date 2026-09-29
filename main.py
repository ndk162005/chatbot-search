"""
Main entry point for the PDF AI Assistant.

This application exposes:

    /api/query
    /api/upload
    /api/documents

and serves the frontend.
"""

import sys
from pathlib import Path

# Automatically attach .venv site-packages if running with global Python interpreter
BASE_DIR = Path(__file__).resolve().parent
venv_site_packages = BASE_DIR / ".venv" / "Lib" / "site-packages"
if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
    sys.path.insert(0, str(venv_site_packages))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    query_router,
    upload_router,
    documents_router,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend" / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_DIR = BASE_DIR / "uploads"

DATA_DIR = BASE_DIR / "data"


# Create required directories
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PDF AI Assistant",
    description=(
        "PDF chatbot and semantic search application."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    query_router
)

app.include_router(
    upload_router
)

app.include_router(
    documents_router
)


# ============================================================
# FRONTEND STATIC FILES
# ============================================================

if FRONTEND_DIR.exists():
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


# ============================================================
# ROOT ROUTE
# ============================================================

@app.get(
    "/",
    include_in_schema=False,
)
async def root():

    index_file = FRONTEND_DIR / "index.html"

    if not index_file.exists():

        return {
            "application": "PDF AI Assistant",
            "status": "running",
        }

    return FileResponse(
        index_file
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
@app.get(
    "/api/health",
    tags=["System"],
)
async def health():

    return {
        "status": "healthy",
        "application": "PDF AI Assistant",
    }


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import os
    import socket
    import uvicorn

    def find_available_port(start_port: int) -> int:
        for p in range(start_port, start_port + 20):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", p))
                    return p
                except OSError:
                    continue
        return start_port

    target_port = int(os.getenv("PORT", "8000"))
    port = find_available_port(target_port)
    if port != target_port:
        print(f"\n[WARNING] Port {target_port} is currently locked or in use. Automatically falling back to free port {port}.")
    print(f"[INFO] Serving PDF AI Assistant on http://127.0.0.1:{port}\n")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False)