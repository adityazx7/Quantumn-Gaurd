"""
api/routers/attacks.py
FastAPI router for Attack Matrix evaluations, SciPy exact bounds, and benchmark sweeps.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from api.services.qkd_service import SHARED_QKD_SERVICE

router = APIRouter(tags=["attacks"])


@router.get("/api/benchmark")
async def get_benchmark() -> Dict[str, Any]:
    """Runs SciPy Chernoff-Hoeffding exact benchmark sweep across L=16 to 1024."""
    try:
        return await SHARED_QKD_SERVICE.run_benchmark_async()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/attack-matrix")
async def get_attack_matrix(L: int = 128) -> List[Dict[str, Any]]:
    """Generates comparison matrix across all 7 attack vectors + baseline."""
    try:
        return await SHARED_QKD_SERVICE.run_attack_matrix_async(L=L)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
