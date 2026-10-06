# QuantumGuard QDS: Full-Stack Engineering Roadmap
**Smart India Hackathon (SIH) Problem Statement ID: 26141**  
**Organization:** Egreen Quanta LLP  
**Repository:** [https://github.com/adityazx7/Quantumn-Gaurd.git](https://github.com/adityazx7/Quantumn-Gaurd.git)

---

## Team Overview & Branch Allocation

To scale **QuantumGuard QDS** into a complete enterprise-grade full-stack architecture, the engineering roadmap is divided across three dedicated focus tracks. Each team member has their own designated Git branch to research, develop, and push their contributions.

| Team Member | Branch Name | Primary Domain | Core Tech Stack |
| :--- | :--- | :--- | :--- |
| **Yash Kharat** | `yash-kharat/frontend-ui` | Frontend, UI/UX & Real-Time Client | React / Next.js, Tailwind CSS, Plotly.js, WebSockets, TypeScript |
| **Yash Chobe** | `yash-chobe/backend-quantum` | Backend Systems, Quantum Physics & API | FastAPI, Qiskit 2.x, SciPy, WebSockets, Pydantic v2, JWT Auth |
| **Dhruv Patil** | `dhruv-patil/database-infra` | Database, State Cache, DevOps & Security | PostgreSQL, SQLAlchemy, Redis, Docker Compose, CI/CD |

---

## 1. Yash Kharat — Frontend, UI/UX & Real-Time Client
**Branch:** `yash-kharat/frontend-ui`  
**Role:** Lead Frontend Engineer & Visualization Specialist

### Objective
Elevate the user interface into a production-grade, highly responsive command center with real-time streaming, interactive quantum state visualizers, and polished design.

### Tech Stack to Use
- **Framework:** React or Next.js (TypeScript recommended)
- **Styling:** Tailwind CSS (Keep the clean white theme with vibrant quantum accents: emerald, cyan, indigo, ruby)
- **Visualizations:** Plotly.js (or Three.js for 3D Bloch sphere), Chart.js / Recharts
- **Icons & UI:** Lucide React, Headless UI / Radix UI
- **Real-Time Communication:** Native WebSockets / Socket.io client

### What to Do (Core Tasks & Deliverables)
1. **Component-Based Architecture:**
   - Modularize the dashboard into clean components: `BlochSphere3D`, `AttackControls`, `TelemetryGauges`, `AuditExplorer`, and `QiskitCircuitViewer`.
2. **Real-Time Telemetry Streaming:**
   - Connect the UI to the backend WebSocket stream so QBER error rates, Bell state collapses, and verification outcomes stream in live as calculations run.
3. **Enhanced 3D Bloch Sphere:**
   - Expand the Bloch sphere view to support multi-qubit navigation, state transitions during teleportation, and visual representation of measurement collapse.
4. **Red-Team vs Blue-Team Studio:**
   - Provide a clean split-screen UX where users can customize attack parameters on the left and see immediate defense telemetry on the right.
5. **Authentication & Session Explorer:**
   - Create clean login/registration views and an interactive filterable view for browsing historical cryptographic ledger blocks.

> **Guidance:** Don't hesitate to research modern dashboard layouts and UX patterns. Keep the UI clean, white-themed, and intuitive for hackathon judges and cryptography researchers.

---

## 2. Yash Chobe — Backend Architecture, Quantum Engine & API
**Branch:** `yash-chobe/backend-quantum`  
**Role:** Backend Architect & Quantum Services Engineer

### Objective
Scale the FastAPI backend into a modular, asynchronous microservice architecture, expand the Qiskit physics simulation capabilities, and handle multi-user cryptographic sessions.

### Tech Stack to Use
- **Core Framework:** FastAPI (Python 3.10+) with Uvicorn
- **Quantum & Math:** Qiskit 2.x, NumPy, SciPy (Strictly No AI/ML in detection logic!)
- **Communication:** FastAPI WebSockets (`/ws/telemetry`)
- **Data Validation & Auth:** Pydantic v2, PyJWT, passlib (bcrypt)
- **Async Processing:** Background tasks / async workers for large $L=1024$ sweeps

### What to Do (Core Tasks & Deliverables)
1. **Modular Service Layer Pattern:**
   - Refactor backend code into clean layers:
     - `routers/` (simulation, attacks, ledger, auth, circuit)
     - `services/` (quantum service, statistical detection service, QKD service)
     - `schemas/` (Pydantic request/response models)
2. **WebSocket Telemetry Streaming:**
   - Create a WebSocket endpoint (`/ws/simulate`) that emits live step-by-step telemetry as each phase of the 5-phase protocol executes.
3. **Advanced Quantum Noise Models in Qiskit:**
   - Expand Qiskit simulations to support realistic quantum noise channels (depolarizing, amplitude damping, phase flip) using Qiskit noise models.
4. **Authentication & Multi-Party Signatures:**
   - Implement JWT-based authentication for distinct cryptographic entities: Alice (Signer), Bob (Verifier 1), and Charlie (Verifier 2).
5. **Rate Limiting & Async Sweeps:**
   - Ensure the server stays responsive during heavy key sweeps ($L \ge 1024$) using asynchronous execution.

> **Guidance:** Research Qiskit 2.x quantum circuit optimization and FastAPI async patterns. Ensure the strict Zero-AI / ITS constraint remains 100% intact across all verification routes.

---

## 3. Dhruv Patil — Database Systems, Distributed Cache & DevOps / Infrastructure
**Branch:** `dhruv-patil/database-infra`  
**Role:** Database Architect & Cloud Infrastructure / DevOps Engineer

### Objective
Build the persistent storage layer, production Redis caching for sub-microsecond key burning, containerize the entire stack, and automate testing via CI/CD.

### Tech Stack to Use
- **Relational Database:** PostgreSQL with SQLAlchemy & Alembic migrations
- **In-Memory Cache:** Redis (for sub-microsecond key invalidation and anti-replay enforcement)
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Web Server / Reverse Proxy:** Nginx (optional) or Docker network bridge

### What to Do (Core Tasks & Deliverables)
1. **PostgreSQL Relational Schema & ORM:**
   - Design and implement database tables with SQLAlchemy:
     - `users` (credentials, entity roles: Signer, Verifier, Auditor)
     - `sessions` (Session IDs, timestamps, message payloads, status)
     - `ledger_blocks` (block index, session ID, hash, previous_hash, QBER, S-value, enforcement level)
     - `telemetry_logs` (historical error rates, basis asymmetry, execution times)
   - Setup Alembic for database migrations.
2. **Production Redis Cache Layer:**
   - Implement real Redis connections (`redis-py` / `aioredis`) replacing the mock in-memory cache.
   - Enforce atomic key invalidation using Redis commands (`SETNX`, `EXPIRE`) to guarantee that measured SIDs can never be re-used across distributed verifier nodes.
3. **Docker & Docker Compose Orchestration:**
   - Create `Dockerfile` for the FastAPI backend and frontend.
   - Write `docker-compose.yml` spinning up the complete stack in one command:
     - `frontend` container
     - `backend` container
     - `postgres` container
     - `redis` container
4. **CI/CD Automation (GitHub Actions):**
   - Create `.github/workflows/ci.yml` to automatically run tests (`test_core.py`, `test_attacks.py`, `test_api.py`) on every push and pull request.
5. **Security & Backup:**
   - Implement cryptographic block integrity checks and automated backup routines.

> **Guidance:** Research optimal Docker multi-stage builds and Redis atomic operations. Ensure the setup is effortless for any judge or evaluator to launch with `docker-compose up`.

---

## Collaboration & Git Workflow

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/adityazx7/Quantumn-Gaurd.git
   cd Quantumn-Gaurd
   ```
2. **Switch to Your Designated Branch:**
   ```bash
   # Yash Kharat:
   git checkout yash-kharat/frontend-ui

   # Yash Chobe:
   git checkout yash-chobe/backend-quantum

   # Dhruv Patil:
   git checkout dhruv-patil/database-infra
   ```
3. **Develop & Commit Frequently:**
   ```bash
   git add .
   git commit -m "feat(scope): descriptive commit message"
   ```
4. **Push to Your Branch:**
   ```bash
   git push origin <your-branch-name>
   ```
5. **Open Pull Requests:**
   When ready to merge a feature into `main`, create a Pull Request on GitHub for team review and testing!
