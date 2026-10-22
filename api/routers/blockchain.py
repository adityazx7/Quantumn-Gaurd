"""
api/routers/blockchain.py
FastAPI router for Web3/EVM Blockchain Integration, EIP-712 Structured Proofs,
Zero-Cost Testnets (Polygon Amoy / Sepolia), and Sub-Cent Gas Estimation.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.blockchain_engine import (
    SHARED_BLOCKCHAIN_ENGINE,
    BLOCKCHAIN_NETWORKS,
    EVMMerkleProofGenerator
)

router = APIRouter(tags=["blockchain"])


class AnchorSimulationRequest(BaseModel):
    session_id: str = Field(default="SESS-QUANTUM-001", description="Unique session ID")
    message_hash: str = Field(default="845f748ef27a58c0e9c815e6a29e8500a103959c110fdeb62e31e349f05dfe4c")
    merkle_root: str = Field(default="0x3fca91b72a819ec4b5d6f8314e1a0b5c7e8d9a2b1c4e6f8a9b0c2d3e4f5a6b7c")
    block_hash: str = Field(default="0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b")
    qber: float = Field(default=0.012, ge=0.0, le=1.0)
    chsh_s: float = Field(default=2.812, ge=0.0, le=4.0)
    decision: str = Field(default="ACCEPTED")
    enforcement_level: str = Field(default="MONITOR")
    network_id: str = Field(default="POLYGON_AMOY_TESTNET")


class MerkleProofRequest(BaseModel):
    leaves: List[str] = Field(
        default=[
            "SWIFT_TRANSFER:10000000_USD:ALICE->BOB",
            "QUANTUM_TELEMETRY:QBER=0.012:CHSH=2.812",
            "CONSENSUS_QUORUM:BOB_ACCEPT:CHARLIE_ACCEPT",
            "NON_REPUDIATION:SESSION_BURNED"
        ]
    )


@router.get("/api/blockchain/networks")
def list_networks() -> List[Dict[str, Any]]:
    """Returns supported zero-cost testnets and sub-cent production networks under $1 budget."""
    return SHARED_BLOCKCHAIN_ENGINE.get_supported_networks()


@router.get("/api/blockchain/estimate-gas")
def estimate_gas_cost(network_id: str = Query("POLYGON_AMOY_TESTNET")) -> Dict[str, Any]:
    """
    Estimates gas fee and USD cost for anchoring a QDS verification block.
    Demonstrates $0.00 cost on testnets and ~$0.003 on Polygon PoS Mainnet.
    """
    if network_id not in BLOCKCHAIN_NETWORKS:
        raise HTTPException(status_code=400, detail=f"Unsupported network: {network_id}")
    return SHARED_BLOCKCHAIN_ENGINE.estimate_transaction_cost(network_id)


@router.post("/api/blockchain/anchor-simulation")
def simulate_on_chain_anchor(req: AnchorSimulationRequest) -> Dict[str, Any]:
    """
    Executes a high-fidelity EVM smart contract anchor simulation for QDSVerifier.sol.
    Enforces contract invariants (QBER <= 12%, CHSH S >= 2.50, anti-replay),
    and generates EIP-712 structured data and receipt.
    """
    try:
        return SHARED_BLOCKCHAIN_ENGINE.simulate_anchor_transaction(
            session_id=req.session_id,
            message_hash=req.message_hash,
            merkle_root=req.merkle_root,
            block_hash=req.block_hash,
            qber=req.qber,
            chsh_s=req.chsh_s,
            decision=req.decision,
            enforcement_level=req.enforcement_level,
            network_id=req.network_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/blockchain/merkle-proof")
def generate_merkle_proof(req: MerkleProofRequest) -> Dict[str, Any]:
    """
    Generates a binary cryptographic Merkle tree and audit inclusion proofs
    compatible with on-chain Solidity verification (OpenZeppelin MerkleProof.sol).
    """
    try:
        return EVMMerkleProofGenerator.generate_merkle_tree_and_proofs(req.leaves)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
