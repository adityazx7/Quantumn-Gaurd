"""
api/routers/pqc.py
FastAPI router for NIST Post-Quantum Cryptography (FIPS 204 ML-DSA, FIPS 205 SLH-DSA),
and 3-Tier Hybrid Quantum-Proof Signing Envelopes.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.post_quantum_crypto import SHARED_PQC_SUITE
from core.real_test_cases import RealTestCaseService

router = APIRouter(tags=["pqc"])


class HybridSignRequest(BaseModel):
    test_case_id: str = Field(default="SWIFT_WIRE_TRANSFER", description="Industry standard test case ID")
    tamper_payload: bool = Field(default=False, description="Whether to tamper with in-flight payload fields")
    custom_message: Optional[str] = None


class HybridVerifyRequest(BaseModel):
    test_case_id: str = Field(default="SWIFT_WIRE_TRANSFER")
    tamper_payload: bool = Field(default=False)
    simulate_shor_quantum_attack: bool = Field(default=False, description="Simulates Shor's algorithm breaking classical Ed25519")
    envelope: Dict[str, Any]


@router.get("/api/pqc/overview")
def get_pqc_standards_overview() -> Dict[str, Any]:
    """Returns metadata for NIST Post-Quantum Cryptography standards ratified in August 2024."""
    return {
        "status": "RATIFIED_NIST_STANDARDS",
        "primary_standards": [
            {
                "standard": "FIPS 204: ML-DSA (Module-Lattice Digital Signatures)",
                "former_name": "CRYSTALS-Dilithium",
                "hardness_assumption": "Module Learning With Errors (M-LWE) & Module Short Integer Solution (M-SIS)",
                "security_category": "NIST Category 2 / 128-bit quantum security",
                "quantum_resistance": "IMMUNE to Shor's algorithm, 128-bit security against Grover's algorithm."
            },
            {
                "standard": "FIPS 205: SLH-DSA (Stateless Hash-Based Digital Signatures)",
                "former_name": "SPHINCS+",
                "hardness_assumption": "Collision-Resistance and Second-Preimage Resistance of SHA-256",
                "security_category": "Zero Number-Theoretic Assumptions",
                "quantum_resistance": "IMMUNE to Shor's algorithm, pure hash-based security."
            },
            {
                "standard": "FIPS 203: ML-KEM (Module-Lattice Key Encapsulation)",
                "former_name": "CRYSTALS-Kyber",
                "hardness_assumption": "Learning With Errors (LWE) over module lattices",
                "security_category": "NIST Category 1, 3, 5",
                "quantum_resistance": "IMMUNE to Shor's algorithm."
            }
        ],
        "hybrid_architecture": "3-Tier Hybrid Defense: Classical Ed25519 + NIST ML-DSA + Pauli-6 MUB QDS"
    }


@router.post("/api/pqc/sign-hybrid")
def sign_payload_hybrid(req: HybridSignRequest) -> Dict[str, Any]:
    """
    Signs a real structured test case payload using the 3-Tier Quantum-Proof Hybrid Envelope:
    - Tier 1: Classical Ed25519 (RFC 8032)
    - Tier 2: Post-Quantum Lattice (NIST FIPS 204 ML-DSA)
    - Tier 3: Quantum Physical Teleportation Signature (Pauli-6 MUBs)
    """
    try:
        prep = RealTestCaseService.prepare_test_case_payload(
            case_id=req.test_case_id,
            apply_tampering=req.tamper_payload
        )
        canonical_str = prep["active_canonical_str"]

        envelope = SHARED_PQC_SUITE.sign_hybrid_envelope(
            payload_canonical_str=canonical_str,
            qds_session_id=f"HYB-QDS-{int(prep['original_digest'][:8], 16)}",
            qds_qber=0.012 if not req.tamper_payload else 0.375,
            qds_decision="ACCEPTED" if not req.tamper_payload else "REJECTED"
        )

        return {
            "test_case_info": {
                "id": prep["case_id"],
                "name": prep["case_name"],
                "category": prep["category"],
                "standard": prep["standard"],
                "active_digest": prep["active_digest"],
                "tampered": prep["tamper_info"]["tampered"],
                "tamper_narrative": prep["tamper_info"]["attack_narrative"]
            },
            "hybrid_envelope": envelope
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/pqc/verify-hybrid")
def verify_payload_hybrid(req: HybridVerifyRequest) -> Dict[str, Any]:
    """
    Verifies 3-Tier hybrid signature envelope and simulates Shor's algorithm breaking
    classical discrete-log ECC while NIST ML-DSA and QDS Pauli eigenstates remain unbreakable.
    """
    try:
        prep = RealTestCaseService.prepare_test_case_payload(
            case_id=req.test_case_id,
            apply_tampering=req.tamper_payload
        )
        canonical_str = prep["active_canonical_str"]

        verification_result = SHARED_PQC_SUITE.verify_hybrid_envelope(
            payload_canonical_str=canonical_str,
            envelope=req.envelope,
            simulate_shor_quantum_attack=req.simulate_shor_quantum_attack
        )

        return {
            "test_case_id": req.test_case_id,
            "tampered": req.tamper_payload,
            "shor_attack_simulated": req.simulate_shor_quantum_attack,
            "verification_result": verification_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
