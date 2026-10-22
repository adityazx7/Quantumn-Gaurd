"""
api/schemas/simulation.py
Pydantic v2 schemas for QDS simulation requests, responses, benchmarks, test cases, and blockchain anchoring.
"""
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

ValidAttackType = Literal[
    "NONE", "FORGERY", "IMPERSONATION", "INTERCEPT_RESEND",
    "REPLAY", "UNAUTHORIZED_PROBE", "WEAK_INTERCEPT", "REPUDIATION",
    "PNS_ATTACK"
]

class SimulationRequest(BaseModel):
    message: str = Field(default="Quantum Authenticated Transaction Payload", min_length=1, description="Payload message or digest to sign")
    L: int = Field(default=64, ge=16, le=1024, description="Quantum key length in qubits")
    attack_type: ValidAttackType = Field(
        default="NONE",
        description="Attack scenario: NONE, FORGERY, IMPERSONATION, INTERCEPT_RESEND, REPLAY, UNAUTHORIZED_PROBE, WEAK_INTERCEPT, REPUDIATION, PNS_ATTACK"
    )
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.30, description="Optical channel depolarizing noise probability")
    sid: Optional[str] = Field(default=None, description="Optional Session Identifier for anti-replay tracking")
    test_case_id: Optional[str] = Field(default=None, description="Optional structured test case: SWIFT_WIRE_TRANSFER, EIP712_SMART_CONTRACT, SCADA_GRID_SWITCHING, CCSDS_SATELLITE_TELECOMMAND, HL7_FHIR_MEDICAL, JWT_OAUTH2_AUTH")
    tamper_payload: bool = Field(default=False, description="Whether to simulate active field-level payload tampering")
    eavesdrop_fraction: float = Field(default=1.0, ge=0.01, le=1.0, description="Adversary eavesdropping tap ratio eta")
    adversary_basis: str = Field(default="Z", description="Adversary intercept basis: Z, X, Y, or RANDOM")


class AdversarySimulateRequest(BaseModel):
    attack_type: str = Field(default="FORGERY", description="Adversarial vector: FORGERY, INTERCEPT_RESEND, IMPERSONATION, REPLAY, WEAK_INTERCEPT, UNAUTHORIZED_PROBE, REPUDIATION, PNS_ATTACK")
    test_case_id: str = Field(default="SWIFT_WIRE_TRANSFER", description="Real-world target test case ID")
    eavesdrop_fraction: float = Field(default=1.0, ge=0.01, le=1.0, description="Eavesdropping tap percentage eta")
    adversary_basis: str = Field(default="Z", description="Measurement basis chosen by adversary: Z, X, Y, RANDOM")
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.30, description="Background optical fiber noise floor")
    L: int = Field(default=64, ge=16, le=1024, description="Quantum signature key length in qubits")
    custom_message: Optional[str] = Field(default=None, description="Optional custom payload override")
    sid: Optional[str] = Field(default=None, description="Optional Session ID")


class TestCaseExecuteRequest(BaseModel):
    test_case_id: str = Field(default="SWIFT_WIRE_TRANSFER", description="Target test case: SWIFT_WIRE_TRANSFER, EIP712_SMART_CONTRACT, SCADA_GRID_SWITCHING, CCSDS_SATELLITE_TELECOMMAND, HL7_FHIR_MEDICAL, JWT_OAUTH2_AUTH")
    tamper_payload: bool = Field(default=False, description="Simulate selective payload field tampering")
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.30, description="Channel noise probability")
    L: int = Field(default=64, ge=16, le=1024, description="Qubit key length")


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
    blockchain_contract: str = "contracts/QDSVerifier.sol"
