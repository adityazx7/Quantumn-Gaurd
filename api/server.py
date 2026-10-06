"""
server.py
Layer 3: FastAPI REST Server & Telemetry Orchestrator
Exposes endpoints for Qiskit quantum circuit simulation, SciPy Chernoff-Hoeffding bounds,
Grover weak disturbance amplification, multi-receiver consensus, and cryptographic audit ledger.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from core.attack_simulator import AdversarialAttackSimulator
from core.security_proofs import SecurityProofEngine
from core.qds_teleport_core import QiskitCircuitBuilder

app = FastAPI(
    title="QuantumGuard QDS: Quantum-Inspired Cyber Threat Detection",
    description="4-Layer Zero-AI Teleportation-based Quantum Digital Signature Verification Framework (SIH 26141)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = AdversarialAttackSimulator()


class SimulationRequest(BaseModel):
    message: str = Field(default="Quantum Authenticated Transaction Payload")
    L: int = Field(default=64, ge=16, le=1024)
    attack_type: str = Field(default="NONE")
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.30)
    sid: Optional[str] = None


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    return {
        "status": "ONLINE",
        "problem_statement_id": "26141",
        "organization": "Egreen Quanta LLP",
        "architecture": "4-Layer Zero-AI Quantum-Inspired Architecture (Qiskit + SciPy + FastAPI + Plotly)",
        "security_basis": "Information-Theoretic Security (No-Cloning, MUBs, Bell Monogamy, Hoeffding Bounds)",
        "active_cache_count": simulator.state_cache.get_consumed_count(),
        "ledger_block_height": len(simulator.audit_ledger.chain),
        "ledger_integrity_valid": simulator.audit_ledger.verify_integrity()
    }


@app.post("/api/simulate")
def run_simulation(req: SimulationRequest) -> Dict[str, Any]:
    try:
        result = simulator.run_pipeline(
            message=req.message,
            L=req.L,
            attack_type=req.attack_type,
            channel_noise=req.channel_noise,
            sid=req.sid
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmark")
def get_benchmark() -> Dict[str, Any]:
    try:
        return simulator.generate_benchmark_sweep()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/attack-matrix")
def get_attack_matrix(L: int = 128) -> List[Dict[str, Any]]:
    try:
        return simulator.generate_attack_comparison_matrix(L=L)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qiskit-circuit")
def get_qiskit_circuit(basis: str = 'X', eigenvalue: int = 1) -> Dict[str, Any]:
    """Returns ASCII diagram and gate counts of the authentic Qiskit teleportation circuit."""
    try:
        circuit_text = QiskitCircuitBuilder.get_circuit_ascii(basis, eigenvalue)
        qc = QiskitCircuitBuilder.create_teleportation_circuit(basis, eigenvalue)
        ops = qc.count_ops()
        return {
            "basis": basis,
            "eigenvalue": eigenvalue,
            "qubits": qc.num_qubits,
            "clbits": qc.num_clbits,
            "gate_counts": dict(ops),
            "circuit_ascii": circuit_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit-ledger")
def get_audit_ledger() -> Dict[str, Any]:
    """Returns the immutable cryptographic audit ledger with chained SHA-256 blocks."""
    return {
        "total_blocks": len(simulator.audit_ledger.chain),
        "integrity_verified": simulator.audit_ledger.verify_integrity(),
        "chain": simulator.audit_ledger.get_all_blocks()
    }


@app.post("/api/audit-ledger/reset")
def reset_ledger() -> Dict[str, str]:
    simulator.state_cache.reset()
    simulator.audit_ledger.reset()
    return {"message": "Microsecond cache and Cryptographic Audit Ledger successfully reset."}


@app.get("/api/security-report")
def get_security_report() -> Dict[str, Any]:
    return SecurityProofEngine.get_security_proof_report()


# Mount static assets
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
