# QuantumGuard QDS: Quantum-Inspired Cyber Threat Detection for Digital Signature Security
**Smart India Hackathon (SIH) Problem Statement ID: 26141**  
**Organization:** Egreen Quanta LLP  
**Repository:** [https://github.com/adityazx7/Quantumn-Gaurd.git](https://github.com/adityazx7/Quantumn-Gaurd.git)  
**Architecture:** 4-Layer Zero-AI Teleportation-based Quantum Digital Signature Framework  
**Tech Stack:** Qiskit 2.5 &bull; NumPy &bull; SciPy &bull; FastAPI &bull; In-Memory Microsecond Cache &bull; SHA-256 Chained Audit Ledger &bull; Plotly.js 3D

---

## 1. Project Overview & Background

As quantum computing advances, classical asymmetric cryptosystems (such as **RSA** and **ECDSA/ECC**) are vulnerable to **Shor's algorithm**, which solves prime factorization and discrete logarithms in polynomial time. This exposes critical global digital infrastructures—such as banking settlements, HTTPS certificates, blockchain consensus, and defense communication—to signature forgery and impersonation.

**Quantum Digital Signature (QDS)** protocols provide **Information-Theoretic Security (ITS)** guaranteed by fundamental quantum mechanics:
- **No-Cloning Theorem:** An unknown quantum key cannot be cloned or copied for offline trial-and-error attacks.
- **Heisenberg Uncertainty & Mutually Unbiased Bases (MUBs):** Measuring a quantum state in an incorrect basis introduces an unavoidable, measurable $\ge 25\% - 33.3\%$ error rate.
- **Bell Monogamy of Entanglement:** Maximal entanglement cannot be shared with an eavesdropper without collapsing correlation.

### The "Zero-AI / Non-ML" Mandate (SIH 26141)
Problem Statement 26141 from **Egreen Quanta LLP** strictly prohibits artificial intelligence or machine learning techniques:
- Machine learning models (CNNs, LSTMs, VQCs) are heuristic and produce false positives and false negatives.
- AI models cannot provide formal **Information-Theoretic Security (ITS)** proofs.
- Instead, this platform uses **exact quantum statevector mechanics, rank-1 projective measurements, and Chernoff–Hoeffding statistical threshold bounds**.

For the exhaustive mathematical and component-by-component manual, see [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md).

---

## 2. Quickstart: How to Download & Run

### Prerequisites
- **Git:** Installed on your machine ([Download Git](https://git-scm.com/))
- **Python 3.10+** (Python 3.11, 3.12, 3.13 supported): ([Download Python](https://www.python.org/downloads/))

---

### Step 1: Clone the Repository
Open PowerShell, Command Prompt, or Terminal:
```bash
git clone https://github.com/adityazx7/Quantumn-Gaurd.git
cd Quantumn-Gaurd
```

---

### Step 2: Create and Activate a Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Dependencies
Install the required scientific, quantum, and web packages:
```bash
pip install -r requirements.txt
```

*Installed Packages include:*
- `qiskit>=2.5.0` (Quantum circuit simulation & teleportation)
- `numpy>=2.0.0` (Fast quantum linear algebra)
- `scipy>=1.14.0` (Exact Chernoff-Hoeffding statistical bounds & CDFs)
- `fastapi>=0.110.0` (Asynchronous high-speed REST telemetry orchestrator)
- `uvicorn>=0.28.0` (ASGI server)
- `pydantic>=2.0.0` & `starlette>=0.36.0`

---

### Step 4: Run the Interactive Command Center
Launch the complete platform with a single command:
```bash
python run.py
```
This automatically boots the FastAPI backend server on `http://127.0.0.1:8000` and opens your default web browser to the interactive dashboard.

> If your browser doesn't open automatically, open your browser and navigate to:  
> **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### Step 5: Run Automated Verification Tests
You can run the three built-in test suites to verify that the quantum physics engine, threat detection algorithms, and API endpoints are working properly:

```bash
# 1. Test Qiskit & Quantum Teleportation Fidelity (100% Deterministic Acceptance)
python tests/test_core.py

# 2. Test All 7 Red-Team Cyber Threat Scenarios & SciPy Exact Bounds
python tests/test_attacks.py

# 3. Test Full REST API, Qiskit Circuit Endpoint & Cryptographic Audit Ledger
python tests/test_api.py
```

---

## 3. 4-Layer Quantum-Inspired Architecture

```
+---------------------------------------------------------------------------------------------------------------+
| LAYER 1: QUANTUM SIMULATION & PHYSICS ENGINE                                                                  |
| - Qiskit 2.5: Native Quantum Circuits (H, CX, X, Z gates) for 6-state Pauli prep and Bell teleportation       |
| - NumPy: Ultra-fast statevector and density-matrix linear algebra for L=1024 sweeps                           |
| - CHSH Bell Inequality Evaluator: Decoy pairs evaluated at {0, pi/4, pi/8, 3pi/8} (Quantum S = 2.828)         |
+---------------------------------------------------------------------------------------------------------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------------------+
| LAYER 2: STATISTICAL THREAT DETECTION (THE "ZERO-AI" BRAIN)                                                  |
| - SciPy: Exact Binomial CDF and normal distribution modeling for Chernoff-Hoeffding bounds                    |
| - Rank-1 Projective Measurements: Pi_pass = |psi><psi|; Empirical QBER across Pauli bases (sigma_x, y, z)      |
| - Grover Weak Disturbance Amplifier: Rotates amplitudes to catch subtle 12% fiber taps                       |
| - Cross-Verifier Consensus Engine: Evaluates Bob vs Charlie state overlap ECS_BC                              |
| - STRICT ZERO-AI RULE: Zero scikit-learn or machine learning dependencies in the detection pipeline           |
+---------------------------------------------------------------------------------------------------------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------------------+
| LAYER 3: BACKEND API & CRYPTOGRAPHIC LEDGER                                                                   |
| - FastAPI: High-performance asynchronous REST endpoints orchestrating simulations and telemetry               |
| - Microsecond State Cache: Sub-microsecond key invalidation preventing Replay Attacks (< 1 microsecond)       |
| - Cryptographic Audit Ledger: Chained SHA-256 blocks for immutable audit trail                                 |
+---------------------------------------------------------------------------------------------------------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------------------+
| LAYER 4: RED-TEAM / BLUE-TEAM COMMAND CENTER DASHBOARD                                                        |
| - Plotly.js (v2.35): Interactive 3D Bloch Sphere with statevector trajectories and Pauli poles                 |
| - Plotly Analytics: Live multi-basis QBER charts, SciPy CDF curves, and O(L) runtime benchmark plots          |
| - Red-Team vs Blue-Team UI: White modern background with colorful accents (emerald, indigo, rose, cyan)       |
+---------------------------------------------------------------------------------------------------------------+
```

---

## 4. Comprehensive 7-Attack Threat Matrix

| Threat Vector | Attack Mechanism | Quantum / Physical Invariant | Mathematical Trigger Rule | Adaptive Enforcement |
| :--- | :--- | :--- | :--- | :---: |
| **0. Legitimate** | Honest Alice & Bob | Max entanglement ($S = 2.828$), noiseless fidelity $F=1.000$ | $\text{QBER} \le T_v$ ($12\%$) & $S \ge 2.50$ | **`MONITOR`** |
| **1. Digital Forgery** | Altered message $M \to M'$ and key guessing | 3 MUBs guess success is $2/3$, inducing $33.3\%$ error | $\text{QBER} \ge T_f$ ($15.0\%$) | **`ISOLATE`** |
| **2. Impersonation** | Eve poses as Alice without Bell entanglement | Reduced density matrix is maximally mixed ($\rho_B = I/2$) | $\text{QBER} \approx 50\%$ across all bases & $S \le 2.0$ | **`ISOLATE`** |
| **3. Channel MitM** | Intercept-resend in preferred basis ($Z$) | Entanglement broken; 50% conjugate basis asymmetry | $\max \|E_\alpha - E_\beta\| \ge \delta_{\text{asym}}$ & $S < 2.50$ | **`ISOLATE`** |
| **4. Transcript Replay** | Reusing intercepted valid transcript $(M, SID)$ | Wavefunction collapse: register physically consumed | $SID \in \text{MicrosecondCache}$ ($P_{\text{detect}} = 1.0$) | **`ISOLATE`** |
| **5. Canary Probe** | Verifier probes register before Alice signs | Measurement-Disturbance reduces state purity $\text{Tr}(\rho^2) < 1.0$ | $\text{Tr}(\rho^2) \le 1 - \epsilon_p$ & $E_{\text{canary}} \ge T_{\text{probe}}$ | **`QUARANTINE`** |
| **6. Weak Intercept** | Subtle fiber tap ($12\%$ of qubits) | Raw QBER is low ($3\%-5\%$), amplified by Grover operator | $\text{Grover\_Amplified\_Score} \ge T_f$ | **`QUARANTINE`** |
| **7. Repudiation** | Alice sends conflicting states to Bob vs Charlie | Cross-verifier state overlap drops | $ECS_{BC} < 0.85$ | **`ISOLATE`** |

---

## 5. Web Command Center Features

1. **Plotly.js 3D Interactive Bloch Sphere:**
   - Real-time 3D unit sphere allowing full mouse/touch orbit, rotation, and zoom.
   - Highlights the 6 Pauli poles: $|0\rangle, |1\rangle, |+\rangle, |-\rangle, |+i\rangle, |-i\rangle$.
   - Renders active state vector $|\psi\rangle$ trajectories and measurement collapses.
2. **Red-Team Attack Launcher (Left Panel):**
   - 8 one-click attack triggers.
   - Dynamic sliders for Key Length $L$ ($16$ to $512$ qubits) and fiber channel noise ($0\%$ to $25\%$).
   - Custom message payload input field.
3. **Blue-Team Defense Console (Right Panel):**
   - Live Adaptive Enforcement badge (`MONITOR`, `RESTRICT`, `QUARANTINE`, `ISOLATE`).
   - Live QBER gauge with animated threshold bars.
   - CHSH Bell inequality gauge ($S = 2.8284$ max quantum vs $2.000$ classical limit).
   - Cross-Verifier Consensus gauge ($ECS_{BC}$) verifying Bob and Charlie agree.
   - Grover Weak Anomaly Amplifier card showing raw error vs amplified energy.
4. **Qiskit Circuit Inspector Modal:**
   - Displays the exact 3-qubit teleportation circuit drawn by Qiskit with gate count statistics ($H, CX, X, Z$).
5. **Chained SHA-256 Audit Ledger:**
   - Real-time view of verified blocks with previous hash chaining and JSON export.

---

## 6. Project File Hierarchy

```
Quantumn-Gaurd/
├── api/
│   ├── __init__.py
│   └── server.py                 # FastAPI REST API & Static File Server
├── core/
│   ├── __init__.py
│   ├── qds_teleport_core.py      # Layer 1: Qiskit 2.5 + NumPy Teleportation Engine
│   ├── threat_detector_stat.py   # Layer 2: SciPy Chernoff-Hoeffding & Non-AI Threat Detection
│   ├── attack_simulator.py       # Layer 3: Red-Team Attack Simulation Suite
│   ├── state_registry.py         # Layer 3: Microsecond Key Cache & SHA-256 Chained Ledger
│   └── security_proofs.py        # Layer 4: Mathematical ITS Proof Report
├── static/
│   └── index.html                # Layer 4: Plotly 3D Bloch Sphere & Command Center UI
├── tests/
│   ├── test_core.py              # Teleportation fidelity tests (F = 1.000000)
│   ├── test_attacks.py           # 7-Attack classification & benchmark tests
│   └── test_api.py               # REST API & static serving integration tests
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python package dependencies
├── run.py                        # One-click launch script
├── PROJECT_COMPLETE_GUIDE.md     # Deep mathematical & component reference manual
├── README.md                     # This README
├── Document 3.pdf                # Architectural specification
├── Document 4.pdf                # Research paper analysis & adaptations
└── SIH26141.pdf                  # Official SIH problem statement document
```

---

## 7. Performance: QDS vs Classical PKI

| Feature / Metric | Classical RSA-2048 | Classical ECC (ECDSA-256) | QuantumGuard QDS (This Framework) |
| :--- | :--- | :--- | :--- |
| **Security Foundation** | Integer Factorization | Discrete Logarithm | **Information-Theoretic Security (Quantum Physics)** |
| **Shor's Algorithm Threat** | **BROKEN** in polynomial time | **BROKEN** in polynomial time | **UNCONDITIONALLY IMMUNE** |
| **Verification Complexity** | $O(k^3)$ modular exponentiation | $O(k^3)$ scalar point multiplication | **$O(L)$ Strict Linear Classical Inner Products** |
| **Verification Latency ($L=128$)** | ~3.5 ms | ~1.5 ms | **< 0.20 ms (Sub-millisecond software runtime)** |
| **False Rejection Rate ($P_{\text{reject}}$)** | Heuristic / N/A | Heuristic / N/A | **$< 10^{-9}$ under Chernoff–Hoeffding bounds** |
| **Forgery Probability ($L=256$)** | Vulnerable to Shor's | Vulnerable to Shor's | **$P_{\text{forge}} < 8.33 \times 10^{-46}$** |

---

## 8. License & Acknowledgements

Developed for **Smart India Hackathon (SIH) Problem Statement ID 26141** sponsored by **Egreen Quanta LLP**.  
Licensed under the Apache 2.0 / MIT License.
