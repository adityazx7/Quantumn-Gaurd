"""
api/routers/circuit.py
FastAPI router for Qiskit circuit analysis, gate counts, and realistic noise simulations.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from api.schemas.circuit import CircuitResponse, NoiseSimulationRequest, NoiseSimulationResponse
from api.services.quantum_service import QuantumSimulationService
from core.security_proofs import SecurityProofEngine

router = APIRouter(tags=["circuit"])


@router.get("/api/qiskit-circuit")
def get_qiskit_circuit(basis: str = 'X', eigenvalue: int = 1) -> Dict[str, Any]:
    """Returns ASCII diagram and gate counts of authentic Qiskit teleportation circuit."""
    try:
        return QuantumSimulationService.get_circuit_details(basis=basis, eigenvalue=eigenvalue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/circuit/noise-simulation")
def simulate_circuit_noise(req: NoiseSimulationRequest) -> Dict[str, Any]:
    """
    Executes Qiskit Aer simulation under physical quantum noise channels:
    - Depolarizing
    - Amplitude Damping (T1 energy relaxation)
    - Phase Damping (T2 pure dephasing)
    - Bit-Flip (Pauli X)
    - Phase-Flip (Pauli Z)
    """
    try:
        return QuantumSimulationService.simulate_noisy_circuit(
            basis=req.basis,
            eigenvalue=req.eigenvalue,
            noise_type=req.noise_type,
            error_rate=req.error_rate,
            shots=req.shots
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/security-report")
def get_security_report() -> Dict[str, Any]:
    """Returns mathematical security proof derivations and complexity bounds."""
    return SecurityProofEngine.get_security_proof_report()
