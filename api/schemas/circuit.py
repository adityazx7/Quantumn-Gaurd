"""
api/schemas/circuit.py
Pydantic v2 schemas for Qiskit circuit inspection and advanced quantum noise modeling.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CircuitRequest(BaseModel):
    basis: str = Field(default="X", description="Pauli basis: 'X', 'Y', 'Z'")
    eigenvalue: int = Field(default=1, description="Eigenvalue: +1 or -1")


class CircuitResponse(BaseModel):
    basis: str
    eigenvalue: int
    qubits: int
    clbits: int
    gate_counts: Dict[str, int]
    circuit_ascii: str


class NoiseSimulationRequest(BaseModel):
    basis: str = Field(default="X", description="Pauli basis: 'X', 'Y', 'Z'")
    eigenvalue: int = Field(default=1, description="Eigenvalue: +1 or -1")
    noise_type: str = Field(
        default="depolarizing",
        description="Noise channel: 'depolarizing', 'amplitude_damping', 'phase_damping', 'bit_flip', 'phase_flip'"
    )
    error_rate: float = Field(default=0.05, ge=0.0, le=0.5, description="Physical error rate / damping probability")
    shots: int = Field(default=1024, ge=100, le=8192, description="Simulation measurement shots")


class NoiseSimulationResponse(BaseModel):
    noise_type: str
    error_rate: float
    shots: int
    ideal_fidelity: float
    noisy_fidelity: float
    purity: float
    statevector_bloch: Dict[str, float]
    measurement_counts: Dict[str, int]
    channel_description: str
