"""
run.py
Main entry point for QuantumGuard QDS Platform.
Problem Statement ID: 26141 (Egreen Quanta LLP)
Quantum-Inspired Cyber Threat Detection for Digital Signature Security.
"""

import sys
import os
import socket
import webbrowser
import threading
import time
import uvicorn

def find_available_port(start_port=8000, max_attempts=20) -> int:
    env_port = os.environ.get("PORT")
    if env_port:
        return int(env_port)
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port

def open_browser(port: int):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"[*] Opening QuantumGuard QDS Dashboard in your web browser: {url}")
    webbrowser.open(url)

def main():
    port = find_available_port(start_port=8000)

    print("=" * 80)
    print("  QUANTUM-INSPIRED CYBER THREAT DETECTION FOR DIGITAL SIGNATURE SECURITY")
    print("  Smart India Hackathon (SIH) Problem Statement ID: 26141")
    print("  Organization: Egreen Quanta LLP")
    print("  Architecture: Zero-AI / Information-Theoretic Teleportation-based QDS")
    print("=" * 80)
    print("\n[*] Deliverables Active:")
    print("  [D1] Quantum Teleportation & QDS Simulation Engine (qds_teleport_core)")
    print("  [D2] Non-AI Statistical Threat Detection & Verification (threat_detector_stat)")
    print("  [D3] Adversarial Attack Simulation Suite (attack_simulator)")
    print("  [D4] Mathematical Modelling & Security Proof Engine (security_proofs)")
    print("  [D5] Interactive Security Telemetry & Verification Dashboard (FastAPI + Web UI)")
    print("  [+] Modular Microservice Routers & PyJWT Multi-Party Cryptographic Sessions")
    print("  [+] Qiskit 2.x Advanced Quantum Noise Models (Aer Depolarizing, T1 & T2 Damping)")
    print(f"\n[*] Starting FastAPI Server on http://127.0.0.1:{port} ...")

    # Start browser launcher in a daemon thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("api.server:app", host="127.0.0.1", port=port, log_level="info", reload=False)

if __name__ == "__main__":
    main()
