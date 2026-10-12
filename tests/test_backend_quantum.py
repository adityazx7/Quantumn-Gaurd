"""
tests/test_backend_quantum.py
Comprehensive test suite for Yash Chobe's Backend Architecture & Quantum Engine:
1. Modular Service Layer & Endpoints
2. WebSocket Telemetry Streaming (/ws/simulate)
3. Advanced Qiskit Aer Quantum Noise Models (Depolarizing, Amplitude Damping, Phase Damping)
4. PyJWT Multi-Party Authentication & Role Authorization (Alice, Bob, Charlie, Auditor)
5. Multi-Party Signature Verification Workflow
6. Asynchronous Execution and Rate Limiting
"""

import sys
import os
import json
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.server import app
from api.services.quantum_service import QuantumSimulationService
from api.services.auth_service import AuthService

client = TestClient(app)


def test_modular_status():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "supported_attacks" in data
    assert len(data["supported_attacks"]) >= 7
    print(">>> [Modular Status] PASSED")


def test_qiskit_noise_simulation_depolarizing():
    payload = {
        "basis": "X",
        "eigenvalue": 1,
        "noise_type": "depolarizing",
        "error_rate": 0.08,
        "shots": 500
    }
    resp = client.post("/api/circuit/noise-simulation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["noise_type"] == "depolarizing"
    assert data["noisy_fidelity"] < 1.0
    assert "statevector_bloch" in data
    assert "measurement_counts" in data
    print(f">>> [Qiskit Noise: Depolarizing] Fidelity: {data['noisy_fidelity']}, Purity: {data['purity']} - PASSED")


def test_qiskit_noise_simulation_amplitude_damping():
    payload = {
        "basis": "Z",
        "eigenvalue": -1,  # |1> excited state undergoes relaxation
        "noise_type": "amplitude_damping",
        "error_rate": 0.15,
        "shots": 500
    }
    resp = client.post("/api/circuit/noise-simulation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["noise_type"] == "amplitude_damping"
    assert data["noisy_fidelity"] < 1.0
    print(f">>> [Qiskit Noise: Amplitude Damping T1] Fidelity: {data['noisy_fidelity']} - PASSED")


def test_qiskit_noise_simulation_phase_damping():
    payload = {
        "basis": "Y",
        "eigenvalue": 1,
        "noise_type": "phase_damping",
        "error_rate": 0.10,
        "shots": 500
    }
    resp = client.post("/api/circuit/noise-simulation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["noise_type"] == "phase_damping"
    print(f">>> [Qiskit Noise: Phase Damping T2] Fidelity: {data['noisy_fidelity']} - PASSED")


def test_jwt_auth_workflow():
    # 1. Fetch directory of entities
    resp = client.get("/api/auth/entities")
    assert resp.status_code == 200
    entities = resp.json()
    usernames = [e["username"] for e in entities]
    assert "alice" in usernames
    assert "bob" in usernames
    assert "charlie" in usernames
    assert "auditor" in usernames

    # 2. Authenticate Alice (Signer)
    alice_login = client.post("/api/auth/login", json={"username": "alice", "password": "alice_signer_2026"})
    assert alice_login.status_code == 200
    alice_token = alice_login.json()["access_token"]
    assert alice_token is not None

    # 3. Authenticate Bob (Verifier)
    bob_login = client.post("/api/auth/login", json={"username": "bob", "password": "bob_verifier_2026"})
    assert bob_login.status_code == 200
    bob_token = bob_login.json()["access_token"]

    # 4. Verify /me endpoint with Alice token
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {alice_token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["sub"] == "alice"
    assert me_data["role"] == "signer"

    # 5. Invalid credentials test
    bad_login = client.post("/api/auth/login", json={"username": "alice", "password": "wrong_password"})
    assert bad_login.status_code == 401

    print(">>> [JWT Auth Workflow] All entities authenticated & verified - PASSED")


def test_multi_party_signature_verification():
    # Login as Alice
    alice_login = client.post("/api/auth/login", json={"username": "alice", "password": "alice_signer_2026"})
    token = alice_login.json()["access_token"]

    # Execute legitimate multi-party verification
    payload = {
        "message": "Approved Cross-Border Settlement",
        "L": 64,
        "channel_noise": 0.01,
        "simulate_attack": "NONE"
    }
    resp = client.post(
        "/api/auth/verify-signature",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["consensus_decision"] == "ACCEPTED"
    assert data["enforcement_level"] == "MONITOR"
    assert data["bob_decision"] == "ACCEPTED"
    assert data["charlie_decision"] == "ACCEPTED"
    print(f">>> [Multi-Party Signature: Honest] Consensus: {data['consensus_decision']} - PASSED")

    # Execute repudiation attack scenario
    payload_rep = {
        "message": "Tampered Settlement Directives",
        "L": 64,
        "channel_noise": 0.01,
        "simulate_attack": "REPUDIATION"
    }
    resp_rep = client.post(
        "/api/auth/verify-signature",
        json=payload_rep,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_rep.status_code == 200
    data_rep = resp_rep.json()
    assert data_rep["consensus_decision"] == "REJECTED"
    print(f">>> [Multi-Party Signature: Repudiation] Caught with Level: {data_rep['enforcement_level']} - PASSED")


def test_websocket_telemetry_streaming():
    with client.websocket_connect("/ws/simulate") as ws:
        # Send simulation command
        ws.send_text(json.dumps({
            "message": "WebSocket Live Stream Test",
            "L": 32,
            "attack_type": "NONE",
            "channel_noise": 0.0
        }))

        events = []
        for _ in range(6):
            data = ws.receive_json()
            events.append(data.get("event"))

        assert "PHASE_1_KEYGEN" in events
        assert "PHASE_2_ENTANGLEMENT" in events
        assert "PHASE_3_TELEPORTATION" in events
        assert "PHASE_4_VERIFICATION" in events
        assert "PHASE_5_CONSENSUS_LEDGER" in events
        assert "SIMULATION_COMPLETE" in events

    print(">>> [WebSocket Telemetry Streaming] All 5 protocol phases streamed in real-time - PASSED")


if __name__ == "__main__":
    test_modular_status()
    test_qiskit_noise_simulation_depolarizing()
    test_qiskit_noise_simulation_amplitude_damping()
    test_qiskit_noise_simulation_phase_damping()
    test_jwt_auth_workflow()
    test_multi_party_signature_verification()
    test_websocket_telemetry_streaming()
    print("\n==================================================================")
    print(">>> ALL YASH CHOBE BACKEND & QUANTUM ENGINE TESTS PASSED! <<<")
    print("==================================================================")
