"""
FastAPI backend — Global Intelligence API.

Runs alongside the Streamlit dashboard on port 8000.
Exposes all intelligence data as JSON endpoints optimized for
a future React/Next.js premium frontend.

Start:  uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import events, intel, map as map_routes, ws
from app.storage.database import init_db

app = FastAPI(
    title="AI Chief Agent API",
    description="Global Intelligence Command Center — Backend API",
    version="1.0.0",
)

# CORS — allow React dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React CRA / Next.js
        "http://localhost:5173",     # Vite
        "http://localhost:8501",     # Streamlit
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# Register route modules
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(intel.router, prefix="/api", tags=["Intelligence"])
app.include_router(map_routes.router, prefix="/api", tags=["Map"])
app.include_router(ws.router, prefix="/api", tags=["WebSocket"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ai-chief-agent"}
