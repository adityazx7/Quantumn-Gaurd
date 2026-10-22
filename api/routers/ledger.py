"""
api/routers/ledger.py
FastAPI router for immutable SHA-256 Cryptographic Audit Ledger, Merkle trees,
smart contract anchoring, and blockchain integrity verification.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from api.services.qkd_service import SHARED_SIMULATOR

router = APIRouter(tags=["ledger"])


@router.get("/api/audit-ledger")
def get_audit_ledger() -> Dict[str, Any]:
    """Returns the immutable cryptographic audit ledger with chained SHA-256 blocks and Merkle roots."""
    return {
        "total_blocks": len(SHARED_SIMULATOR.audit_ledger.chain),
        "integrity_verified": SHARED_SIMULATOR.audit_ledger.verify_integrity(),
        "chain": SHARED_SIMULATOR.audit_ledger.get_all_blocks(),
        "smart_contract": "contracts/QDSVerifier.sol"
    }


@router.get("/api/audit-ledger/verify")
def verify_ledger_integrity() -> Dict[str, Any]:
    """Verifies that all chained cryptographic hashes and Merkle roots are 100% valid."""
    is_valid = SHARED_SIMULATOR.audit_ledger.verify_integrity()
    return {
        "status": "VALID" if is_valid else "CORRUPTED_OR_TAMPERED",
        "integrity_verified": is_valid,
        "total_blocks": len(SHARED_SIMULATOR.audit_ledger.chain),
        "latest_block_hash": SHARED_SIMULATOR.audit_ledger.get_latest_block()["hash"]
    }


@router.post("/api/audit-ledger/tamper-test")
def simulate_ledger_tampering(block_index: int = 1, fake_qber: float = 0.50) -> Dict[str, Any]:
    """
    Demonstrates blockchain tamper-evidence: intentionally alters a historical block
    and proves that verify_integrity() immediately catches the compromise.
    """
    if block_index >= len(SHARED_SIMULATOR.audit_ledger.chain):
        raise HTTPException(status_code=400, detail="Block index does not exist yet. Run a simulation first.")

    success = SHARED_SIMULATOR.audit_ledger.simulate_tamper(
        block_index=block_index,
        target_field="qber",
        fake_value=fake_qber
    )
    is_valid_after = SHARED_SIMULATOR.audit_ledger.verify_integrity()
    return {
        "tamper_injected": success,
        "block_index": block_index,
        "integrity_verified_after_tamper": is_valid_after,
        "tamper_detected": not is_valid_after,
        "verdict": "BLOCKCHAIN_TAMPER_DETECTED" if not is_valid_after else "TAMPER_FAILED"
    }


@router.get("/api/audit-ledger/solidity-calldata/{block_index}")
def export_solidity_calldata(block_index: int) -> Dict[str, Any]:
    """Exports a verified block formatted for on-chain anchoring in QDSVerifier.sol."""
    calldata = SHARED_SIMULATOR.audit_ledger.export_solidity_calldata(block_index)
    if not calldata:
        raise HTTPException(status_code=404, detail=f"Block {block_index} not found.")
    return {
        "block_index": block_index,
        "calldata": calldata,
        "contract": "QDSVerifier.sol",
        "function_signature": "verifyAndSettleSignature(QDSVerificationProof calldata proof)"
    }


@router.post("/api/audit-ledger/reset")
def reset_ledger() -> Dict[str, str]:
    """Resets the microsecond state cache and initializes fresh genesis block."""
    SHARED_SIMULATOR.state_cache.reset()
    SHARED_SIMULATOR.audit_ledger.reset()
    return {"message": "Microsecond cache and Cryptographic Audit Ledger successfully reset."}
