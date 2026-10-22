"""
tests/test_high_level_stack.py
Validates High-Level Blockchain, Post-Quantum Cryptography, and Enterprise Cybersecurity:
1. Zero-Cost Testnets (Polygon Amoy / Ethereum Sepolia) and Sub-Cent Mainnet Gas Calculation (< $1 Budget).
2. EIP-712 Typed Data Verification & Binary Merkle Proofs for QDSVerifier.sol.
3. NIST FIPS 204 ML-DSA & FIPS 205 SLH-DSA Post-Quantum Signatures.
4. 3-Tier Hybrid Defense (Classical Ed25519 + NIST ML-DSA + Pauli QDS) & Shor's Algorithm Simulation.
5. ArcSight CEF Syslog Telemetry, OASIS STIX 2.1 Threat Intel, and Zero-Trust Firewall Rule Playbooks.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient

from api.server import app
from core.blockchain_engine import SHARED_BLOCKCHAIN_ENGINE, EVMMerkleProofGenerator
from core.post_quantum_crypto import SHARED_PQC_SUITE, NIST_ML_DSA, NIST_SLH_DSA, Classical_Ed25519
from core.cybersecurity_soc import SHARED_SOC_ENGINE

client = TestClient(app)


# =========================================================================
# 1. BLOCKCHAIN & GAS COST BUDGET TESTS ($0.00 / < $1.00)
# =========================================================================

def test_blockchain_networks_budget_compliance():
    """Verify testnets cost $0.00 and Polygon mainnet is ~$0.003 (well within $1 limit)."""
    networks = SHARED_BLOCKCHAIN_ENGINE.get_supported_networks()
    assert len(networks) == 4

    # Polygon Amoy Testnet (Free)
    amoy_cost = SHARED_BLOCKCHAIN_ENGINE.estimate_transaction_cost("POLYGON_AMOY_TESTNET")
    assert amoy_cost["is_free_testnet"] is True
    assert amoy_cost["estimated_cost_usd"] == 0.00
    assert "APPROVED (Zero Cost)" in amoy_cost["budget_compliance"]["status"]

    # Polygon PoS Mainnet (< $1.00)
    poly_cost = SHARED_BLOCKCHAIN_ENGINE.estimate_transaction_cost("POLYGON_POS_MAINNET")
    assert poly_cost["is_free_testnet"] is False
    assert poly_cost["estimated_cost_usd"] < 0.01  # Less than 1 cent!
    assert poly_cost["budget_compliance"]["transactions_affordable_for_one_dollar"] >= 200


def test_merkle_proof_generation_and_leaves():
    """Verify binary Merkle tree proofs for smart contract inclusion verification."""
    leaves = [
        "TX_SWIFT_TRANSFER_10M",
        "QBER_METRIC_0.012",
        "CHSH_BELL_S_2.812",
        "CONSENSUS_VERIFIED_QUORUM"
    ]
    tree_result = EVMMerkleProofGenerator.generate_merkle_tree_and_proofs(leaves)
    assert tree_result["root"].startswith("0x")
    assert len(tree_result["proofs"]) == 4
    for leaf in leaves:
        proof = tree_result["proofs"][leaf]["merkle_proof"]
        assert len(proof) >= 2
        for p in proof:
            assert p.startswith("0x")


def test_on_chain_anchor_simulation_valid_and_revert():
    """Verify on-chain contract invariants (accepts healthy states, reverts on high QBER or replayed session)."""
    # 1. Healthy block anchor
    res_valid = SHARED_BLOCKCHAIN_ENGINE.simulate_anchor_transaction(
        session_id="SESS-CHAIN-001",
        message_hash="0xaabbccdd11223344",
        merkle_root="0x1122334455667788",
        block_hash="0x556677889900aabb",
        qber=0.012,
        chsh_s=2.812,
        decision="ACCEPTED",
        enforcement_level="MONITOR",
        network_id="POLYGON_AMOY_TESTNET"
    )
    assert res_valid["transaction_receipt"]["status"] == "SUCCESS (0x1)"
    assert res_valid["transaction_receipt"]["contract_reverted"] is False
    assert res_valid["transaction_receipt"]["event_emitted"]["event"] == "SessionVerifiedAndAnchored"

    # 2. High QBER (> 12%) causes smart contract revert
    res_revert = SHARED_BLOCKCHAIN_ENGINE.simulate_anchor_transaction(
        session_id="SESS-CHAIN-002",
        message_hash="0xaabbccdd11223344",
        merkle_root="0x1122334455667788",
        block_hash="0x556677889900aabb",
        qber=0.35,  # 35% QBER!
        chsh_s=2.812,
        decision="REJECTED",
        enforcement_level="ISOLATE",
        network_id="POLYGON_AMOY_TESTNET"
    )
    assert res_revert["transaction_receipt"]["status"] == "REVERTED"
    assert res_revert["transaction_receipt"]["contract_reverted"] is True
    assert "exceeded maximum security threshold" in res_revert["transaction_receipt"]["revert_reason"]


# =========================================================================
# 2. POST-QUANTUM CRYPTOGRAPHY & HYBRID ENVELOPE TESTS
# =========================================================================

def test_nist_ml_dsa_lattice_signature():
    """Verify NIST FIPS 204 ML-DSA key generation and signing."""
    ml_dsa = NIST_ML_DSA()
    kp = ml_dsa.generate_keypair()
    assert kp["algorithm"] == "NIST_ML_DSA_44"
    assert kp["standard"] == "FIPS 204 (Ratified August 2024)"

    msg = b"EIP-712 PermitTransferFrom: 2,500,000 USDC"
    sig = ml_dsa.sign(msg)
    assert sig["signature_len_bytes"] == 2420
    assert ml_dsa.verify(msg, sig, kp["fingerprint"]) is True

    # Tampered message must fail verification
    assert ml_dsa.verify(b"Tampered Message", sig, kp["fingerprint"]) is False


def test_hybrid_envelope_and_shor_algorithm_resilience():
    """Verify 3-Tier hybrid envelope defends against Shor's algorithm breaking classical Ed25519."""
    suite = SHARED_PQC_SUITE
    payload = '{"amount":"10000000","beneficiary":"CH9300762011623852957890"}'
    
    envelope = suite.sign_hybrid_envelope(
        payload_canonical_str=payload,
        qds_session_id="SESS-HYB-888",
        qds_qber=0.010,
        qds_decision="ACCEPTED"
    )
    assert "tier1_classical_signature" in envelope
    assert "tier2_pqc_lattice_signature" in envelope
    assert "tier3_quantum_physical_signature" in envelope

    # Baseline verification
    res_normal = suite.verify_hybrid_envelope(payload, envelope, simulate_shor_quantum_attack=False)
    assert res_normal["overall_valid"] is True
    assert res_normal["tier1_classical"]["valid"] is True
    assert res_normal["tier2_post_quantum_lattice"]["valid"] is True

    # Under Shor's Algorithm attack: Classical Ed25519 is broken, but PQC Lattice + QDS maintain security!
    res_shor = suite.verify_hybrid_envelope(payload, envelope, simulate_shor_quantum_attack=True)
    assert res_shor["tier1_classical"]["valid"] is False
    assert "Broken by Shor" in res_shor["tier1_classical"]["status"]
    assert res_shor["tier2_post_quantum_lattice"]["valid"] is True
    assert res_shor["survives_ftqc_shor_attack"] is True


# =========================================================================
# 3. ENTERPRISE SOC / SIEM & ACTIVE DEFENSE TESTS
# =========================================================================

def test_cef_syslog_and_stix_threat_intel():
    """Verify ArcSight CEF syslog generation and STIX 2.1 bundles."""
    cef = SHARED_SOC_ENGINE.format_cef_event(
        session_id="SESS-CEF-99",
        threat_type="QUANTUM_MITM_EAVESDROPPING",
        enforcement_level="ISOLATE",
        qber=0.25,
        chsh_s=2.012,
        mitre_technique_id="T1557.002"
    )
    assert cef.startswith("CEF:0|EgreenQuanta|QuantumGuard-QDS|2.0.0|")
    assert "externalId=SESS-CEF-99" in cef
    assert "cs1=T1557.002" in cef

    stix = SHARED_SOC_ENGINE.generate_stix_21_bundle(
        session_id="SESS-STIX-01",
        attack_type="INTERCEPT_RESEND",
        mitre_id="T1557.002",
        mitre_name="Quantum Man-in-the-Middle",
        threat_description="Eavesdropper intercepts teleportation channel.",
        qber=0.25,
        enforcement="ISOLATE"
    )
    assert stix["type"] == "bundle"
    assert len(stix["objects"]) == 3


def test_zero_trust_firewall_playbook_generation():
    """Verify automated generation of iptables, Cisco ACL, and SDN OpenFlow rules."""
    playbook = SHARED_SOC_ENGINE.generate_active_firewall_playbook(
        session_id="SESS-INCIDENT-404",
        threat_type="FORGERY_DETECTED",
        enforcement_level="ISOLATE",
        adversary_ip="198.51.100.99",
        affected_optical_port="TenGigE0/1/0/2"
    )
    assert len(playbook["iptables_commands"]) >= 3
    assert any("198.51.100.99 -j DROP" in cmd for cmd in playbook["iptables_commands"])
    assert any("shutdown" in cmd for cmd in playbook["cisco_acl_commands"])
    assert playbook["sdn_openflow_flowmod"]["actions"] == []  # OpenFlow DROP


# =========================================================================
# 4. FASTAPI ENDPOINT INTEGRATION TESTS
# =========================================================================

def test_api_blockchain_and_pqc_endpoints():
    """Verify /api/blockchain/* and /api/pqc/* endpoints."""
    # Blockchain networks
    resp_net = client.get("/api/blockchain/networks")
    assert resp_net.status_code == 200
    assert len(resp_net.json()) == 4

    # Blockchain gas estimation
    resp_gas = client.get("/api/blockchain/estimate-gas?network_id=POLYGON_AMOY_TESTNET")
    assert resp_gas.status_code == 200
    assert resp_gas.json()["estimated_cost_usd"] == 0.00

    # PQC overview
    resp_pqc = client.get("/api/pqc/overview")
    assert resp_pqc.status_code == 200
    assert "ML-DSA" in str(resp_pqc.json())

    # Hybrid sign endpoint
    resp_sign = client.post("/api/pqc/sign-hybrid", json={
        "test_case_id": "SWIFT_WIRE_TRANSFER",
        "tamper_payload": False
    })
    assert resp_sign.status_code == 200
    sign_data = resp_sign.json()
    assert "hybrid_envelope" in sign_data
    assert sign_data["test_case_info"]["tampered"] is False

    # SOC active defense endpoint
    resp_soc = client.post("/api/soc/active-defense", json={
        "session_id": "SESS-API-TEST",
        "threat_type": "QUANTUM_MITM_EAVESDROPPING",
        "enforcement_level": "ISOLATE",
        "adversary_ip": "203.0.113.5",
        "affected_optical_port": "TenGigE0/1/0/1"
    })
    assert resp_soc.status_code == 200
    assert "iptables_commands" in resp_soc.json()
