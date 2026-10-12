"""
api/schemas/ledger.py
Pydantic v2 schemas for Cryptographic Audit Ledger.
"""
from typing import Dict, Any, List
from pydantic import BaseModel


class LedgerBlock(BaseModel):
    index: int
    timestamp: float
    session_id: str
    message: str
    decision: str
    threat_detected: str
    enforcement_level: str
    qber: float
    chsh_s: float
    previous_hash: str
    block_hash: str


class LedgerResponse(BaseModel):
    total_blocks: int
    integrity_verified: bool
    chain: List[Dict[str, Any]]


class LedgerResetResponse(BaseModel):
    message: str
