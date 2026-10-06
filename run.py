"""
run.py
Main entry point for QuantumGuard QDS Platform.
Problem Statement ID: 26141 (Egreen Quanta LLP)
Quantum-Inspired Cyber Threat Detection for Digital Signature Security.
"""

import sys
import os
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"[*] Opening QuantumGuard QDS Dashboard in your web browser: {url}")
    webbrowser.open(url)

def main():
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
    print("\n[*] Starting FastAPI Server on http://127.0.0.1:8000 ...")

    # Start browser launcher in a daemon thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, log_level="info", reload=False)

if __name__ == "__main__":
    main()
