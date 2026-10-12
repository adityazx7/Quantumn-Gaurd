"""
api/schemas/simulation.py
Pydantic v2 schemas for QDS simulation requests, responses, benchmarks, and statuses.
"""
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

ValidAttackType = Literal[
    "NONE", "FORGERY", "IMPERSONATION", "INTERCEPT_RESEND",
    "REPLAY", "UNAUTHORIZED_PROBE", "WEAK_INTERCEPT", "REPUDIATION"
]

class SimulationRequest(BaseModel):
    message: str = Field(default="Quantum Authenticated Transaction Payload", min_length=1, description="Payload message to sign")
    L: int = Field(default=64, ge=16, le=1024, description="Quantum key length in qubits")
    attack_type: ValidAttackType = Field(
        default="NONE",
        description="Attack scenario: NONE, FORGERY, IMPERSONATION, INTERCEPT_RESEND, REPLAY, UNAUTHORIZED_PROBE, WEAK_INTERCEPT, REPUDIATION"
    )
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.30, description="Optical channel depolarizing noise probability")
    sid: Optional[str] = Field(default=None, description="Optional Session Identifier for anti-replay tracking")


class DecisionInfo(BaseModel):
    decision: str
    threat_type: str
    confidence: float
    enforcement_level: str
    enforcement_action: str
    action_description: str
    audit_block_id: Optional[str] = None


class SimulationResponse(BaseModel):
    status: str
    session_id: str
    key_length: int
    attack_simulated: str
    channel_noise: float
    timestamp: float
    decision: Dict[str, Any]
    qber_analysis: Dict[str, Any]
    chsh_test: Dict[str, Any]
    grover_amplification: Dict[str, Any]
    cross_verifier_consensus: Dict[str, Any]
    bloch_coordinates_teleported: Dict[str, float]
    quantum_audit_ledger: Dict[str, Any]
    execution_time_ms: float


class BenchmarkResponse(BaseModel):
    key_lengths: List[int]
    latencies_ms: List[float]
    theoretical_p_forge: List[float]
    scipy_exact_p_forge: List[float]
    rsa_2048_comparison_ms: List[float]


class AttackMatrixItem(BaseModel):
    attack_code: str
    attack_name: str
    decision: str
    enforcement_level: str
    detected_threat: str
    qber: float
    chsh_s: float
    confidence: float
    grover_amplified: bool
    rejection_rationale: str


class StatusResponse(BaseModel):
    status: str
    problem_statement_id: str
    organization: str
    architecture: str
    security_basis: str
    active_cache_count: int
    ledger_block_height: int
    ledger_integrity_valid: bool
    supported_attacks: List[str]
