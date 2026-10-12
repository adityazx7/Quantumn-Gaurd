"""
api/routers/ledger.py
FastAPI router for immutable SHA-256 Cryptographic Audit Ledger inspection and reset.
"""

from typing import Dict, Any
from fastapi import APIRouter

from api.services.qkd_service import SHARED_SIMULATOR

router = APIRouter(tags=["ledger"])


@router.get("/api/audit-ledger")
def get_audit_ledger() -> Dict[str, Any]:
    """Returns the immutable cryptographic audit ledger with chained SHA-256 blocks."""
    return {
        "total_blocks": len(SHARED_SIMULATOR.audit_ledger.chain),
        "integrity_verified": SHARED_SIMULATOR.audit_ledger.verify_integrity(),
        "chain": SHARED_SIMULATOR.audit_ledger.get_all_blocks()
    }


@router.post("/api/audit-ledger/reset")
def reset_ledger() -> Dict[str, str]:
    """Resets the microsecond state cache and initializes fresh genesis block."""
    SHARED_SIMULATOR.state_cache.reset()
    SHARED_SIMULATOR.audit_ledger.reset()
    return {"message": "Microsecond cache and Cryptographic Audit Ledger successfully reset."}
