"""
api/routers/simulation.py
FastAPI router for QDS simulation pipeline, system status, and live WebSocket telemetry streaming.
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from api.schemas.simulation import SimulationRequest, SimulationResponse, StatusResponse
from api.services.qkd_service import SHARED_SIMULATOR, SHARED_QKD_SERVICE
from core.threat_detector_stat import CHSHEvaluator

router = APIRouter(tags=["simulation"])


@router.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Returns runtime telemetry, active microsecond cache count, and ledger block height."""
    return {
        "status": "ONLINE",
        "problem_statement_id": "26141",
        "organization": "Egreen Quanta LLP",
        "architecture": "4-Layer Zero-AI Quantum-Inspired Architecture (Qiskit + SciPy + FastAPI + WebSockets)",
        "security_basis": "Information-Theoretic Security (No-Cloning, MUBs, Bell Monogamy, Hoeffding Bounds)",
        "active_cache_count": SHARED_SIMULATOR.state_cache.get_consumed_count(),
        "ledger_block_height": len(SHARED_SIMULATOR.audit_ledger.chain),
        "ledger_integrity_valid": SHARED_SIMULATOR.audit_ledger.verify_integrity(),
        "supported_attacks": [
            "NONE", "FORGERY", "IMPERSONATION", "INTERCEPT_RESEND",
            "REPLAY", "UNAUTHORIZED_PROBE", "WEAK_INTERCEPT", "REPUDIATION"
        ]
    }


@router.post("/api/simulate")
async def run_simulation(req: SimulationRequest) -> Dict[str, Any]:
    """
    Executes the 5-phase Zero-AI QDS verification pipeline asynchronously.
    """
    try:
        result = await SHARED_QKD_SERVICE.run_simulation_async(
            message=req.message,
            L=req.L,
            attack_type=req.attack_type,
            channel_noise=req.channel_noise,
            sid=req.sid,
            test_case_id=req.test_case_id,
            tamper_payload=req.tamper_payload,
            eavesdrop_fraction=req.eavesdrop_fraction,
            adversary_basis=req.adversary_basis
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive client parameters
            raw_data = await websocket.receive_text()
            try:
                params = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON format payload"})
                continue

            message = params.get("message", "Live WebSocket Telemetry Payload")
            L = int(params.get("L", 64))
            attack_type = params.get("attack_type", "NONE")
            channel_noise = float(params.get("channel_noise", 0.01))
            sid = params.get("sid", None)
            test_case_id = params.get("test_case_id", None)
            tamper_payload = bool(params.get("tamper_payload", False))
            eavesdrop_fraction = float(params.get("eavesdrop_fraction", 1.0))
            adversary_basis = params.get("adversary_basis", "RANDOM")

            # Phase 1: Key Generation & Pauli Eigenstate Preparation
            await websocket.send_json({
                "event": "PHASE_1_KEYGEN",
                "phase": 1,
                "description": "Alice CSPRNG Secret Key Generation & Pauli State Preparation",
                "data": {
                    "L": L,
                    "bases_alphabet": ["X", "Y", "Z"],
                    "eigenvalues": [+1, -1],
                    "status": "Alice prepared L quantum states in 6-state Pauli alphabet."
                }
            })
            await asyncio.sleep(0.08)

            # Phase 2: EPR Entanglement Distribution & CHSH Witness
            chsh_result = CHSHEvaluator.simulate_chsh_test(
                num_pairs=min(L, 100),
                channel_depolarizing=channel_noise,
                is_entangled=(attack_type not in ["IMPERSONATION", "INTERCEPT_RESEND"])
            )
            await websocket.send_json({
                "event": "PHASE_2_ENTANGLEMENT",
                "phase": 2,
                "description": "Bell Pair Entanglement Distribution & CHSH Bell Inequality Witness",
                "data": {
                    "chsh_s_value": chsh_result["S_value"],
                    "bell_violated": chsh_result["bell_inequality_violated"],
                    "entanglement_verified": chsh_result["entanglement_verified"]
                }
            })
            await asyncio.sleep(0.08)

            # Phase 3: Quantum Teleportation Channel Execution
            await websocket.send_json({
                "event": "PHASE_3_TELEPORTATION",
                "phase": 3,
                "description": "Alice Bell Joint Measurement & Bob Unitary Pauli Corrections",
                "data": {
                    "protocol": "3-Qubit Quantum Teleportation",
                    "channel_noise": channel_noise,
                    "simulated_attack": attack_type
                }
            })
            await asyncio.sleep(0.08)

            # Phase 4 & 5: Statistical Verification & Final Result
            result = await SHARED_QKD_SERVICE.run_simulation_async(
                message=message,
                L=L,
                attack_type=attack_type,
                channel_noise=channel_noise,
                sid=sid,
                test_case_id=test_case_id,
                tamper_payload=tamper_payload,
                eavesdrop_fraction=eavesdrop_fraction,
                adversary_basis=adversary_basis
            )

            qber_data = result.get("qber_analysis", {})
            hoeffding = result.get("hoeffding_bounds", {})
            await websocket.send_json({
                "event": "PHASE_4_VERIFICATION",
                "phase": 4,
                "description": "Non-AI Statistical Verification (QBER, Asymmetry, Hoeffding Bounds)",
                "data": {
                    "qber": qber_data.get("qber", 0.0),
                    "threshold_Tv": hoeffding.get("T_v", 0.04),
                    "basis_asymmetry": qber_data.get("delta_asymmetry", 0.0),
                    "grover_amplification": result.get("grover_amplification", {})
                }
            })
            await asyncio.sleep(0.08)

            await websocket.send_json({
                "event": "PHASE_5_CONSENSUS_LEDGER",
                "phase": 5,
                "description": "Multi-Receiver Consensus & Chained SHA-256 Audit Ledger Block Creation",
                "data": {
                    "decision": result["decision"]["decision"],
                    "threat_type": result["decision"]["threat_type"],
                    "enforcement_level": result["decision"]["enforcement_level"],
                    "audit_block_id": result["decision"].get("audit_block_id")
                }
            })

            await websocket.send_json({
                "event": "SIMULATION_COMPLETE",
                "phase": 6,
                "result": result
            })

    except WebSocketDisconnect:
        pass


@router.websocket("/ws/simulate")
async def websocket_simulate_endpoint(websocket: WebSocket):
    """Real-time streaming telemetry endpoint for interactive dashboards."""
    await _handle_websocket_telemetry(websocket)


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Alias for /ws/simulate for dashboard telemetry."""
    await _handle_websocket_telemetry(websocket)
