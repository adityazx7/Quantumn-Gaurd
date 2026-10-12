"""
api/server.py
Modular Asynchronous FastAPI Microservice Architecture for QuantumGuard QDS.
Smart India Hackathon (SIH) Problem Statement ID: 26141 (Egreen Quanta LLP).
Refactored by Yash Chobe (Backend Architect & Quantum Services Engineer):
- Modular Layered Routers: simulation, attacks, ledger, circuit, auth
- WebSocket Telemetry Streaming (/ws/simulate, /ws/telemetry)
- Qiskit 2.x Advanced Quantum Noise Models (Depolarizing, Amplitude Damping, Phase Damping)
- PyJWT Multi-Party Cryptographic Entity Authentication (Alice, Bob, Charlie, Auditor)
- Sliding-Window Rate Limiting & Asynchronous Simulation Sweeps
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.services.qkd_service import SHARED_SIMULATOR
from api.schemas.simulation import SimulationRequest
from api.middleware.rate_limiter import RateLimiterMiddleware
from api.routers import (
    simulation_router,
    attacks_router,
    ledger_router,
    circuit_router,
    auth_router
)

# Export simulator for backward compatibility with external scripts/tests
simulator = SHARED_SIMULATOR

app = FastAPI(
    title="QuantumGuard QDS: Quantum-Inspired Cyber Threat Detection",
    description="Modular Zero-AI Teleportation-based Quantum Digital Signature Framework (SIH 26141)",
    version="2.5.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Rate Limiter Middleware for heavy quantum operations
app.add_middleware(RateLimiterMiddleware, max_requests_per_minute=200)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Register Modular Routers
app.include_router(simulation_router)
app.include_router(attacks_router)
app.include_router(ledger_router)
app.include_router(circuit_router)
app.include_router(auth_router)

# Mount Static Dashboard Files
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
