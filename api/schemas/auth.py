"""
api/schemas/auth.py
Pydantic v2 schemas for multi-party authentication and signatures.
Cryptographic Entities: Alice (Signer), Bob (Verifier 1), Charlie (Verifier 2), Auditor.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Entity username, e.g., 'alice', 'bob', 'charlie', 'auditor'")
    password: str = Field(..., description="Secret passphrase for entity authentication")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: Dict[str, Any]


class UserEntity(BaseModel):
    username: str
    entity_name: str
    role: str  # "signer", "verifier_1", "verifier_2", "auditor"
    public_key_fingerprint: str
    description: str


class MultiPartyVerifyRequest(BaseModel):
    message: str = Field(default="Smart Contract Settlement Directive", description="Payload signed by Alice")
    L: int = Field(default=64, ge=16, le=512, description="Key length in qubits")
    channel_noise: float = Field(default=0.01, ge=0.0, le=0.20)
    simulate_attack: Optional[str] = Field(default="NONE", description="Simulated attack during multi-party verification")


class MultiPartyVerifyResponse(BaseModel):
    status: str
    session_id: str
    signer: str
    verifiers: List[str]
    bob_decision: str
    bob_qber: float
    charlie_decision: str
    charlie_qber: float
    consensus_decision: str
    enforcement_level: str
    repudiation_risk_score: float
    audit_block_hash: str
