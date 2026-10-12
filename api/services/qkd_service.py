"""
api/services/qkd_service.py
Layer 3 QKD & Multi-Party Signature Coordination Service.
Coordinates the multi-party QDS workflow across Alice, Bob, and Charlie.
Provides asynchronous, non-blocking execution for heavy benchmark sweeps (L=1024).
"""

import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from core.attack_simulator import AdversarialAttackSimulator
from core.state_registry import MicrosecondStateCache, CryptographicAuditLedger
from core.threat_detector_stat import CrossVerifierConsensusEngine

# Shared thread pool executor for CPU-bound quantum simulations
SIMULATION_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="quantum_worker")


class QKDSignatureService:
    """Orchestrates multi-party QDS signatures and asynchronous execution."""

    def __init__(self, simulator: Optional[AdversarialAttackSimulator] = None):
        self.simulator = simulator or AdversarialAttackSimulator()

    async def run_simulation_async(self,
                                   message: str = "Quantum Authenticated Payload",
                                   L: int = 64,
                                   attack_type: str = "NONE",
                                   channel_noise: float = 0.01,
                                   sid: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes quantum simulation asynchronously in worker thread pool.
        Keeps the FastAPI event loop responsive during heavy L=1024 simulations.
        """
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            SIMULATION_EXECUTOR,
            self.simulator.run_pipeline,
            message,
            L,
            attack_type,
            channel_noise,
            sid
        )
        return result

    async def run_benchmark_async(self) -> Dict[str, Any]:
        """Runs the SciPy benchmark sweep asynchronously without blocking server."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            SIMULATION_EXECUTOR,
            self.simulator.generate_benchmark_sweep
        )

    async def run_attack_matrix_async(self, L: int = 128) -> List[Dict[str, Any]]:
        """Runs the attack comparison matrix asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            SIMULATION_EXECUTOR,
            self.simulator.generate_attack_comparison_matrix,
            L
        )

    def execute_multi_party_signature(self,
                                      signer: str = "Alice",
                                      verifiers: Optional[List[str]] = None,
                                      message: str = "Interbank Wire Transfer",
                                      L: int = 64,
                                      channel_noise: float = 0.01,
                                      simulate_attack: str = "NONE") -> Dict[str, Any]:
        """
        Executes full multi-party QDS protocol:
        Alice -> Bob (Verifier 1) and Charlie (Verifier 2).
        Verifies individual QBERs and cross-verifier non-repudiation consensus.
        """
        if verifiers is None:
            verifiers = ["Bob", "Charlie"]

        session_id = f"MPS-SEC-{uuid.uuid4().hex[:12].upper()}"

        # Bob simulation
        bob_sim = self.simulator.run_pipeline(
            message=message,
            L=L,
            attack_type=simulate_attack if simulate_attack != "REPUDIATION" else "NONE",
            channel_noise=channel_noise,
            sid=f"{session_id}-BOB"
        )

        # Charlie simulation (if repudiation attack, Charlie receives altered states)
        charlie_attack = simulate_attack
        charlie_sim = self.simulator.run_pipeline(
            message=message,
            L=L,
            attack_type=charlie_attack,
            channel_noise=channel_noise,
            sid=f"{session_id}-CHARLIE"
        )

        bob_decision = bob_sim["decision"]["decision"]
        bob_qber = bob_sim["qber_analysis"]["qber"]
        charlie_decision = charlie_sim["decision"]["decision"]
        charlie_qber = charlie_sim["qber_analysis"]["qber"]

        # Use consensus result computed by the simulation pipeline
        if simulate_attack == "REPUDIATION":
            ecs = charlie_sim.get("consensus", {})
        else:
            ecs = bob_sim.get("consensus", {})

        consensus_verified = ecs.get("consensus_verified", True)
        repudiation_flag = ecs.get("repudiation_detected", False)

        if bob_decision == "ACCEPTED" and charlie_decision == "ACCEPTED" and consensus_verified:
            consensus_decision = "ACCEPTED"
            enforcement = "MONITOR"
        else:
            consensus_decision = "REJECTED"
            enforcement = "ISOLATE" if repudiation_flag else (bob_sim["decision"]["enforcement_level"])

        # Fetch latest block hash
        latest_block = self.simulator.audit_ledger.chain[-1] if self.simulator.audit_ledger.chain else None
        if isinstance(latest_block, dict):
            block_hash = latest_block.get("hash", latest_block.get("block_hash", "0" * 64))
        elif latest_block and hasattr(latest_block, "block_hash"):
            block_hash = latest_block.block_hash
        else:
            block_hash = "0" * 64

        return {
            "status": "COMPLETED",
            "session_id": session_id,
            "signer": signer,
            "verifiers": verifiers,
            "message": message,
            "bob_decision": bob_decision,
            "bob_qber": round(bob_qber, 4),
            "charlie_decision": charlie_decision,
            "charlie_qber": round(charlie_qber, 4),
            "consensus_decision": consensus_decision,
            "enforcement_level": enforcement,
            "repudiation_risk_score": round(max(0.0, 1.0 - float(ecs.get("ECS_score", 1.0))), 4),
            "cross_verifier_details": ecs,
            "audit_block_hash": block_hash
        }


# Global shared instance
SHARED_SIMULATOR = AdversarialAttackSimulator()
SHARED_QKD_SERVICE = QKDSignatureService(SHARED_SIMULATOR)
