"""
Mehal Lab Inventory System - FastAPI Application
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.routes import auth_routes, inventory_routes, activity_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mehal Lab Inventory System",
    description="Yale School of Medicine - Liver Center",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(inventory_routes.router)
app.include_router(activity_routes.router)


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the inventory frontend."""
    # Check multiple possible locations for the frontend
    search_paths = [
        os.environ.get("FRONTEND_DIR", ""),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend"),
    ]
    
    # If running as frozen exe, also check _MEIPASS
    if getattr(sys, 'frozen', False):
        search_paths.insert(0, os.path.join(sys._MEIPASS, "frontend"))
        search_paths.append(os.path.join(os.path.dirname(sys.executable), "frontend"))

    for base in search_paths:
        html_path = os.path.join(base, "index.html") if not base.endswith("index.html") else base
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())

    return HTMLResponse(
        content="<h1>Mehal Lab Inventory</h1>"
        "<p>Frontend not found. Make sure frontend/index.html exists next to the exe.</p>"
        f"<p>Searched: {search_paths}</p>"
    )


@app.get("/health")
def health():
    return {"status": "running"}
