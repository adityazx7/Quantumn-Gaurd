import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

def test_api_status():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert data["problem_statement_id"] == "26141"
    assert data["ledger_integrity_valid"] is True
    print(">>> /api/status test passed with ledger integrity! <<<")

def test_api_qiskit_circuit():
    resp = client.get("/api/qiskit-circuit?basis=X&eigenvalue=1")
    assert resp.status_code == 200
    data = resp.json()
    assert "circuit_ascii" in data
    assert data["qubits"] == 3
    print(">>> /api/qiskit-circuit test passed! Gate counts:", data["gate_counts"])

def test_api_audit_ledger():
    resp = client.get("/api/audit-ledger")
    assert resp.status_code == 200
    data = resp.json()
    assert data["integrity_verified"] is True
    assert data["total_blocks"] >= 1
    print(f">>> /api/audit-ledger test passed! Blocks: {data['total_blocks']} <<<")

def test_api_simulation_legitimate():
    payload = {
        "message": "Financial Settlement Test",
        "L": 64,
        "attack_type": "NONE",
        "channel_noise": 0.0
    }
    resp = client.post("/api/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"]["decision"] == "ACCEPTED"
    assert data["decision"]["enforcement_level"] == "MONITOR"
    assert data["qber_analysis"]["qber"] == 0.0
    print(f">>> Legitimate simulation verified: Level={data['decision']['enforcement_level']} <<<")

def test_api_all_attacks():
    attacks = [
        "FORGERY", "IMPERSONATION", "INTERCEPT_RESEND", "REPLAY",
        "UNAUTHORIZED_PROBE", "WEAK_INTERCEPT", "REPUDIATION"
    ]
    for atk in attacks:
        payload = {
            "message": "Attack Test Payload",
            "L": 64,
            "attack_type": atk,
            "channel_noise": 0.01
        }
        resp = client.post("/api/simulate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["decision"]["decision"] == "REJECTED" or data["decision"]["enforcement_level"] in ["RESTRICT", "QUARANTINE", "ISOLATE"]
        print(f">>> Attack {atk:<20} caught: {data['decision']['threat_type']} (Level: {data['decision']['enforcement_level']}) <<<")

def test_frontend_static():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "QuantumGuard QDS" in resp.text
    print(">>> Static index.html served successfully with Plotly! <<<")

if __name__ == "__main__":
    test_api_status()
    test_api_qiskit_circuit()
    test_api_audit_ledger()
    test_api_simulation_legitimate()
    test_api_all_attacks()
    test_frontend_static()
    print("\n>>> ALL API & SYSTEM ENDPOINTS VALIDATED WITH DOCUMENT 4 ENHANCEMENTS! <<<")
