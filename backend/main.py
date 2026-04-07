"""
main.py — FastAPI application for the LAPIS dashboard.

Entry point for the backend API server. Provides:
- REST endpoints for presets, pipeline execution, and results
- WebSocket endpoint for real-time pipeline updates
- CORS middleware for frontend communication
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.presets import router as presets_router
from backend.api.pipeline import router as pipeline_router
from backend.api.results import router as results_router
from backend.websocket import handle_websocket

# Configuration
DEBUG = os.environ.get("DEBUG", "").strip() == "1"

# CORS origins (allow frontend dev server and production)
CORS_ORIGINS = [
    "http://localhost:5173",      # Vite dev server (primary)
    "http://localhost:5174",      # Vite fallback port
    "http://localhost:5175",      # Vite fallback port
    "http://localhost:5176",      # Vite fallback port
    "http://localhost:3000",      # Alternative dev port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:3000",
    "http://localhost:8000",      # Same-origin
    "http://localhost:8001",      # Backend port
]

# Add production origin if configured
PRODUCTION_ORIGIN = os.environ.get("LAPIS_FRONTEND_ORIGIN")
if PRODUCTION_ORIGIN:
    CORS_ORIGINS.append(PRODUCTION_ORIGIN)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup - check for API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        print("[LAPIS] Anthropic API key found")
    else:
        print("[LAPIS] Warning: ANTHROPIC_API_KEY not set - Claude models will not work")

    if openai_key:
        print("[LAPIS] OpenAI API key found")
    else:
        print("[LAPIS] Warning: OPENAI_API_KEY not set - GPT models will not work")

    print("[LAPIS] API server starting...")
    yield
    # Shutdown
    print("[LAPIS] API server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="LAPIS API",
    description="Language-to-Action Planning via Iterative Schema injection",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(presets_router)
app.include_router(pipeline_router)
app.include_router(results_router)


# WebSocket endpoint
@app.websocket("/ws/pipeline")
async def websocket_pipeline(websocket: WebSocket):
    """
    WebSocket endpoint for real-time pipeline updates.

    Connect to receive stage-by-stage updates during pipeline execution.
    """
    await handle_websocket(websocket)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "debug": DEBUG,
    }


# API info endpoint
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "LAPIS API",
        "version": "1.0.0",
        "description": "Language-to-Action Planning via Iterative Schema injection",
        "endpoints": {
            "presets": "/api/presets",
            "pipeline": "/api/run",
            "status": "/api/status/{run_id}",
            "results": "/api/results",
            "websocket": "/ws/pipeline",
            "health": "/health",
        },
    }


# Models info endpoint
@app.get("/api/models")
async def get_models():
    """Get available LLM models."""
    return {
        "models": {
            "claude-sonnet-4-6": "Claude Sonnet 4.6",
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o mini",
        },
        "planners": ["pyperplan", "up_fd", "fd"],
    }


# Mount static files for plan animations and results
_RESULTS_DIR = Path(__file__).parent.parent / "results_web"
_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/results", StaticFiles(directory=str(_RESULTS_DIR)), name="results")

# Mount static files for frontend (production mode)
_FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "dist"
if _FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_BUILD), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
    )
