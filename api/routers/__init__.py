"""
api/routers
Modular FastAPI routers for QuantumGuard QDS.
"""
from api.routers.simulation import router as simulation_router
from api.routers.attacks import router as attacks_router
from api.routers.ledger import router as ledger_router
from api.routers.circuit import router as circuit_router
from api.routers.auth import router as auth_router
from api.routers.blockchain import router as blockchain_router
from api.routers.pqc import router as pqc_router
from api.routers.soc import router as soc_router

__all__ = [
    "simulation_router",
    "attacks_router",
    "ledger_router",
    "circuit_router",
    "auth_router",
    "blockchain_router",
    "pqc_router",
    "soc_router",
]
