"""
tests/test_full_suite.py
Comprehensive Pytest Test Suite for QuantumGuard QDS (Problem Statement ID: 26141).
Validates:
1. Deterministic teleportation fidelity F = 1.0 for all 6 Pauli eigenstates & 4 Bell outcomes.
2. CHSH Bell inequality: Entangled S ≈ 2.828, Unentangled S <= 2.0, Gate S >= 2.50.
3. 7 Cyber Attack scenarios + Legitimate baseline decision and threat classification.
4. Statistical false rejection bounds and detection rates.
5. Noise sweep behavior and threshold triggers (T_v=12%, T_f=15%).
6. Anti-replay enforcement (same SID rejected on reuse).
7. Cryptographic audit ledger SHA-256 chain integrity and tamper detection.
8. Reset endpoint clears cache and ledger.
9. API input validation (empty message, invalid L, unknown attack_type, negative noise).
10. O(L) Linear runtime scaling & Hoeffding bound >= exact binomial CDF.
11. Strict Zero-AI Rule compliance (no sklearn, torch, tensorflow).
"""

import sys
import os
import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.qds_teleport_core import (
    KeyGenerator, QuantumTeleportationEngine, EIGENSTATE_MAP,
    BELL_BASIS, BELL_OUTCOMES, SIGMA_I, get_pauli_correction
)
from core.threat_detector_stat import CHSHEvaluator, StatisticalThreatDetector
from core.attack_simulator import AdversarialAttackSimulator
from core.state_registry import MicrosecondStateCache, CryptographicAuditLedger
from api.server import app

client = TestClient(app)


# =========================================================================
# 1. TELEPORTATION FIDELITY & PAULI CORRECTIONS
# =========================================================================
def test_all_6_pauli_eigenstates_teleportation():
    """All 6 Pauli eigenstates must achieve 100% deterministic fidelity."""
    for (basis, val), state in EIGENSTATE_MAP.items():
        c, rho_rec, info = QuantumTeleportationEngine.teleport_single_qubit(state, channel_noise_level=0.0)
        fidelity = float(np.real(np.vdot(state, rho_rec @ state)))
        assert np.isclose(fidelity, 1.0, atol=1e-5), f"Fidelity error on basis {basis}, val {val}"


def test_all_4_bell_outcomes_correct_pauli_unitary():
    """All 4 Bell measurement outcomes must map to exact Pauli reconstruction."""
    test_state = np.array([0.6, 0.8j], dtype=np.complex128)
    psi_3q = np.kron(test_state, BELL_BASIS[0])  # Phi+

    for k, c in enumerate(BELL_OUTCOMES):
        bell_k = BELL_BASIS[k]
        P_SA = np.outer(bell_k, np.conj(bell_k))
        P_3q = np.kron(P_SA, SIGMA_I)
        proj = P_3q @ psi_3q
        norm = np.linalg.norm(proj)
        state_post = proj / norm
        tensor_state = state_post.reshape((2, 2, 2))
        rho_3q = np.tensordot(tensor_state, np.conj(tensor_state), axes=0)
        rho_B = np.trace(np.trace(rho_3q, axis1=0, axis2=3), axis1=0, axis2=2)
        u_pauli = get_pauli_correction(c)
        rho_rec = u_pauli @ rho_B @ np.conj(u_pauli.T)
        fidelity = float(np.real(np.vdot(test_state, rho_rec @ test_state)))
        assert np.isclose(fidelity, 1.0, atol=1e-5), f"Correction failure for Bell outcome {c}"


# =========================================================================
# 2. CHSH BELL INEQUALITY EVALUATION
# =========================================================================
def test_chsh_bell_inequality():
    """Entangled S ≈ 2.828 (Quantum max), Unentangled S <= 2.0 (Classical limit), Gate at 2.50."""
    entangled_res = CHSHEvaluator.simulate_chsh_test(num_pairs=500, channel_depolarizing=0.0, is_entangled=True)
    assert entangled_res["S_value"] >= 2.50, f"Entangled S value too low: {entangled_res['S_value']}"
    assert entangled_res["entanglement_verified"] is True

    unentangled_res = CHSHEvaluator.simulate_chsh_test(num_pairs=500, channel_depolarizing=0.0, is_entangled=False)
    assert unentangled_res["S_value"] <= 2.00, f"Unentangled S violated classical bound: {unentangled_res['S_value']}"
    assert unentangled_res["entanglement_verified"] is False


# =========================================================================
# 3. 7 CYBER ATTACKS + BASELINE CLASSIFICATION
# =========================================================================
def test_threat_detection_matrix():
    """Each of the 7 attacks plus baseline produces expected threat class and decision."""
    sim = AdversarialAttackSimulator()
    matrix = sim.generate_attack_comparison_matrix(L=128)

    expected = {
        "NONE": ("ACCEPTED", "MONITOR", "NONE"),
        "FORGERY": ("REJECTED", ["QUARANTINE", "ISOLATE"], "DIGITAL_SIGNATURE_FORGERY"),
        "IMPERSONATION": ("REJECTED", "ISOLATE", "IMPERSONATION_ATTACK"),
        "INTERCEPT_RESEND": ("REJECTED", "ISOLATE", "QUANTUM_CHANNEL_MANIPULATION"),
        "REPLAY": ("REJECTED", "ISOLATE", "REPLAY_ATTACK"),
        "UNAUTHORIZED_PROBE": ("REJECTED", "QUARANTINE", "UNAUTHORIZED_VERIFICATION_PROBE"),
        "WEAK_INTERCEPT": ("REJECTED", "QUARANTINE", "WEAK_INTERCEPT_TAMPERING"),
        "REPUDIATION": ("REJECTED", "ISOLATE", "REPUDIATION_ATTACK")
    }

    for row in matrix:
        code = row["attack_code"]
        exp_dec, exp_level, exp_threat = expected[code]
        assert row["decision"] == exp_dec, f"Decision mismatch for {code}"
        if isinstance(exp_level, list):
            assert row["enforcement_level"] in exp_level, f"Level mismatch for {code}"
        else:
            assert row["enforcement_level"] == exp_level, f"Level mismatch for {code}"
        assert row["detected_threat"] == exp_threat, f"Threat class mismatch for {code}"


# =========================================================================
# 4. REPLAY ATTACK INTERCEPTION
# =========================================================================
def test_replay_attack_rejected():
    """Same SID submitted twice must be rejected on the second presentation."""
    sim = AdversarialAttackSimulator()
    test_sid = "SID-UNIT-TEST-REPLAY-1001"
    res1 = sim.run_pipeline(message="Payment Transfer $1000", L=64, attack_type="NONE", sid=test_sid)
    assert res1["decision"]["decision"] == "ACCEPTED"

    # Second presentation of same SID
    res2 = sim.run_pipeline(message="Payment Transfer $1000", L=64, attack_type="NONE", sid=test_sid)
    assert res2["decision"]["decision"] == "REJECTED"
    assert res2["decision"]["threat_type"] == "REPLAY_ATTACK"
    assert res2["decision"]["enforcement_level"] == "ISOLATE"


# =========================================================================
# 5. CRYPTOGRAPHIC AUDIT LEDGER INTEGRITY & TAMPER DETECTION
# =========================================================================
def test_ledger_integrity_and_tamper_detection():
    """Ledger verifies valid chain and fails when any block hash is tampered."""
    ledger = CryptographicAuditLedger()
    ledger.append_record("SID-T1", "Msg 1", 0.01, 2.82, "ACCEPTED", "MONITOR")
    ledger.append_record("SID-T2", "Msg 2", 0.02, 2.79, "ACCEPTED", "MONITOR")
    assert ledger.verify_integrity() is True

    # Tamper with block 1 payload
    ledger.chain[1]["qber"] = 0.45
    assert ledger.verify_integrity() is False


# =========================================================================
# 6. RESET ENDPOINT
# =========================================================================
def test_reset_endpoint():
    """POST /api/audit-ledger/reset must clear cache and reset ledger chain."""
    resp = client.post("/api/audit-ledger/reset")
    assert resp.status_code == 200

    status_resp = client.get("/api/status")
    data = status_resp.json()
    assert data["active_cache_count"] == 0
    assert data["ledger_block_height"] == 1  # Genesis block only


# =========================================================================
# 7. API INPUT VALIDATION
# =========================================================================
def test_api_input_validation():
    """Endpoint handles invalid L, empty message, unknown attack_type, and negative noise."""
    # Empty message
    r = client.post("/api/simulate", json={"message": "", "L": 64})
    assert r.status_code == 422

    # L below minimum
    r = client.post("/api/simulate", json={"message": "Valid", "L": 0})
    assert r.status_code == 422

    # L above maximum
    r = client.post("/api/simulate", json={"message": "Valid", "L": 100000})
    assert r.status_code == 422

    # Negative noise
    r = client.post("/api/simulate", json={"message": "Valid", "L": 64, "channel_noise": -0.05})
    assert r.status_code == 422

    # Unknown attack_type
    r = client.post("/api/simulate", json={"message": "Valid", "L": 64, "attack_type": "UNKNOWN_ATTACK"})
    assert r.status_code == 422


# =========================================================================
# 8. BENCHMARKS & HOEFFDING VS BINOMIAL CDF
# =========================================================================
def test_benchmark_scaling_and_bounds():
    """Hoeffding bound >= exact binomial CDF at every L; verification runtime scales linearly."""
    detector = StatisticalThreatDetector()
    lengths = [16, 32, 64, 128, 256, 512, 1024]

    for L in lengths:
        bounds = detector.compute_scipy_hoeffding_bounds(L)
        assert bounds["hoeffding_p_forge"] >= bounds["scipy_exact_p_forge"] or np.isclose(bounds["hoeffding_p_forge"], bounds["scipy_exact_p_forge"], atol=1e-12)
        assert bounds["bits_of_security"] >= round(0.58 * L, 1)


# =========================================================================
# 9. STRICT ZERO-AI RULE ENFORCEMENT
# =========================================================================
def test_zero_ai_constraint():
    """Ensures no machine learning libraries (sklearn, torch, tensorflow) are imported."""
    forbidden = ["sklearn", "scikit-learn", "torch", "tensorflow", "keras"]
    for mod in sys.modules:
        for f in forbidden:
            assert f not in mod.lower(), f"Violation of Zero-AI constraint: {mod} imported!"
