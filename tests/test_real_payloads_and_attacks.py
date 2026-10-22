"""
tests/test_real_payloads_and_attacks.py
Comprehensive test suite validating:
1. Real-world industry test cases (SWIFT, EIP-712, SCADA, CCSDS, HL7, JWT) in legitimate and tampered modes.
2. Advanced Adversarial Attack Simulator with MITRE ATT&CK mappings and variable eavesdrop fraction eta.
3. Cryptographic Blockchain Ledger with Merkle Tree proof generation, tamper detection, and Solidity calldata.
4. FastAPI Endpoints for test cases, adversary profiles, and ledger verification.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from fastapi.testclient import TestClient

from api.server import app
from core.real_test_cases import RealTestCaseService
from core.adversarial_engine import ConfigurableAdversaryEngine
from core.state_registry import CryptographicAuditLedger, MerkleTree
from core.attack_simulator import AdversarialAttackSimulator

client = TestClient(app)


# =========================================================================
# 1. REAL TEST CASES TESTS
# =========================================================================

def test_real_test_cases_catalog():
    """Verify all 6 industry test cases are correctly loaded with schemas."""
    cases = RealTestCaseService.list_test_cases()
    assert len(cases) == 6
    case_ids = [c["id"] for c in cases]
    expected_ids = [
        "SWIFT_WIRE_TRANSFER",
        "EIP712_SMART_CONTRACT",
        "SCADA_GRID_SWITCHING",
        "CCSDS_SATELLITE_TELECOMMAND",
        "HL7_FHIR_MEDICAL",
        "JWT_OAUTH2_AUTH"
    ]
    for eid in expected_ids:
        assert eid in case_ids


def test_canonical_hash_and_tampering():
    """Verify canonical serialization and targeted field-level tampering."""
    case = RealTestCaseService.get_test_case("SWIFT_WIRE_TRANSFER")
    assert case is not None
    orig_str, orig_digest = RealTestCaseService.canonicalize_payload(case["payload"])
    assert len(orig_digest) == 64

    prep_legit = RealTestCaseService.prepare_test_case_payload("SWIFT_WIRE_TRANSFER", apply_tampering=False)
    prep_tamper = RealTestCaseService.prepare_test_case_payload("SWIFT_WIRE_TRANSFER", apply_tampering=True)

    assert prep_legit["active_digest"] == orig_digest
    assert prep_tamper["active_digest"] != orig_digest
    assert prep_tamper["tamper_info"]["tampered"] is True
    assert prep_tamper["tamper_info"]["target_field"] == "beneficiary.account_iban"


def test_real_test_case_execution_legitimate():
    """Verify legitimate real payload passes QDS protocol with ACCEPTED decision."""
    sim = AdversarialAttackSimulator()
    res = sim.run_pipeline(
        L=64,
        attack_type="NONE",
        channel_noise=0.01,
        test_case_id="EIP712_SMART_CONTRACT",
        tamper_payload=False
    )
    assert res["decision"]["decision"] == "ACCEPTED"
    assert res["structured_test_case"]["case_id"] == "EIP712_SMART_CONTRACT"
    assert res["structured_test_case"]["tamper_info"]["tampered"] is False


def test_real_test_case_execution_tampered():
    """Verify tampered real payload is immediately blocked by cryptographic digest mismatch."""
    sim = AdversarialAttackSimulator()
    res = sim.run_pipeline(
        L=64,
        attack_type="NONE",
        channel_noise=0.01,
        test_case_id="SCADA_GRID_SWITCHING",
        tamper_payload=True
    )
    assert res["decision"]["decision"] == "REJECTED"
    assert res["decision"]["threat_type"] == "DIGITAL_SIGNATURE_FORGERY"
    assert res["decision"]["enforcement_level"] == "ISOLATE"
    assert res["structured_test_case"]["tamper_info"]["tampered"] is True


# =========================================================================
# 2. ADVERSARIAL ENGINE & ATTACK PROFILES TESTS
# =========================================================================

def test_adversary_profiles_mitre_mapping():
    """Verify adversary engine exposes 8 profiles mapped to MITRE ATT&CK."""
    profiles = ConfigurableAdversaryEngine.list_attack_profiles()
    assert len(profiles) == 8
    for p in profiles:
        assert "mitre_technique" in p
        assert "mitre_id" in p
        assert p["mitre_id"].startswith("T")


def test_variable_eavesdrop_fraction():
    """Verify eavesdrop fraction eta directly scales measured QBER."""
    engine = ConfigurableAdversaryEngine()
    
    # eta = 0.1 (weak tap)
    res_weak = engine.execute_adversarial_simulation(
        L=128,
        attack_type="WEAK_INTERCEPT",
        eavesdrop_fraction=0.10,
        adversary_basis="Z"
    )
    
    # eta = 1.0 (full intercept-resend)
    res_full = engine.execute_adversarial_simulation(
        L=128,
        attack_type="INTERCEPT_RESEND",
        eavesdrop_fraction=1.00,
        adversary_basis="RANDOM"
    )

    assert res_weak["qber_analysis"]["qber"] < res_full["qber_analysis"]["qber"]
    assert res_full["qber_analysis"]["qber"] >= 0.20  # Theoretical ~25% for full intercept-resend
    assert len(res_full["execution_trace"]) == 6


# =========================================================================
# 3. BLOCKCHAIN AUDIT LEDGER & MERKLE TREE TESTS
# =========================================================================

def test_merkle_tree_construction():
    """Verify binary Merkle tree root and tamper sensitivity."""
    leaves = [
        "tx1:Alice->Bob:100",
        "tx2:Bob->Charlie:50",
        "qber:0.015",
        "s_val:2.812"
    ]
    root = MerkleTree.compute_merkle_root(leaves)
    assert len(root) == 64  # SHA-256 hex string

    # Modifying any leaf must change root
    leaves_modified = list(leaves)
    leaves_modified[0] = "tx1:Alice->Bob:999"
    root_mod = MerkleTree.compute_merkle_root(leaves_modified)
    assert root_mod != root


def test_cryptographic_ledger_tamper_simulation():
    """Verify CryptographicAuditLedger detects simulated data tampering."""
    ledger = CryptographicAuditLedger()
    b1 = ledger.append_record(
        session_id="SESS-001",
        message="Quantum Payload Data",
        qber=0.012,
        chsh_s=2.82,
        decision="ACCEPTED",
        enforcement_level="MONITOR",
        signer="Alice",
        verifiers=["Bob", "Charlie"],
        payload_digest="d41d8cd98f00b204e9800998ecf8427e"
    )
    assert ledger.verify_integrity() is True

    # Simulate block tampering
    tampered = ledger.simulate_tamper(block_index=1, target_field="qber", fake_value=0.50)
    assert tampered is True
    assert ledger.verify_integrity() is False


def test_solidity_calldata_generation():
    """Verify export of EVM ABI-compatible calldata for Ethereum QDSVerifier contract."""
    ledger = CryptographicAuditLedger()
    ledger.append_record(
        session_id="EVM-SESS-777",
        message="EVM Payload",
        qber=0.018,
        chsh_s=2.81,
        decision="ACCEPTED",
        enforcement_level="MONITOR",
        signer="Alice",
        verifiers=["Bob", "Charlie"],
        payload_digest="aabbccddee00112233445566778899aabbccddee00112233445566778899aabb"
    )
    calldata = ledger.export_solidity_calldata(block_index=1)
    assert calldata is not None
    assert calldata["sessionId"] == "EVM-SESS-777"
    assert calldata["messageHash"].startswith("0x")
    assert calldata["merkleRoot"].startswith("0x")
    assert calldata["blockHash"].startswith("0x")
    assert calldata["qberBps"] == 180  # 0.018 * 10000


# =========================================================================
# 4. FASTAPI ENDPOINTS TESTS
# =========================================================================

def test_api_test_cases_endpoints():
    """Verify /api/test-cases and /api/test-cases/execute endpoints."""
    # List test cases
    resp = client.get("/api/test-cases")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 6

    # Execute legitimate
    exec_resp = client.post("/api/test-cases/execute", json={
        "test_case_id": "SWIFT_WIRE_TRANSFER",
        "tamper_payload": False,
        "L": 64,
        "attack_type": "NONE"
    })
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["decision"]["decision"] == "ACCEPTED"
    assert exec_data["structured_test_case"]["tamper_info"]["tampered"] is False

    # Execute tampered
    tamper_resp = client.post("/api/test-cases/execute", json={
        "test_case_id": "SWIFT_WIRE_TRANSFER",
        "tamper_payload": True,
        "L": 64,
        "attack_type": "NONE"
    })
    assert tamper_resp.status_code == 200
    tamper_data = tamper_resp.json()
    assert tamper_data["decision"]["decision"] == "REJECTED"
    assert tamper_data["structured_test_case"]["tamper_info"]["tampered"] is True


def test_api_adversary_endpoints():
    """Verify /api/adversary/profiles and /api/adversary/simulate endpoints."""
    # Profiles
    resp = client.get("/api/adversary/profiles")
    assert resp.status_code == 200
    profiles = resp.json()
    assert isinstance(profiles, list)
    assert len(profiles) == 8

    # Simulate adversary engagement
    sim_resp = client.post("/api/adversary/simulate", json={
        "attack_type": "UNAUTHORIZED_PROBE",
        "eavesdrop_fraction": 0.45,
        "adversary_basis": "RANDOM",
        "tamper_payload": False,
        "L": 64,
        "channel_noise": 0.01
    })
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert "execution_trace" in sim_data
    assert "decision" in sim_data
    assert sim_data["attack_metadata"]["mitre_id"] == "T1056.004"


def test_api_ledger_tamper_test_endpoint():
    """Verify /api/audit-ledger/tamper-test endpoint."""
    # Run a test case simulation first so the ledger has blocks beyond genesis
    client.post("/api/test-cases/execute", json={
        "test_case_id": "JWT_OAUTH2_AUTH",
        "tamper_payload": False,
        "L": 64,
        "attack_type": "NONE"
    })

    resp = client.post("/api/audit-ledger/tamper-test?block_index=1&fake_qber=0.55")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tamper_detected"] is True
    assert data["integrity_verified_after_tamper"] is False
    assert data["verdict"] == "BLOCKCHAIN_TAMPER_DETECTED"
