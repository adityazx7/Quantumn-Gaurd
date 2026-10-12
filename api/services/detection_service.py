"""
api/services/detection_service.py
Layer 2 Statistical Detection Service: Strictly Zero-AI Threat Classification.
Wraps core physics evaluations:
- Bell-CHSH Entanglement Witness Testing (S >= 2.50)
- Chernoff-Hoeffding CDF Tail Bounds & Verification Thresholds (Tv, Tf)
- Grover Weak Disturbance Amplification
- Cross-Verifier Consensus Scheme (ECS)
- Graduated Enforcement Ladder (MONITOR, RESTRICT, QUARANTINE, ISOLATE)
"""

from typing import Dict, Any, List, Optional
from core.threat_detector_stat import (
    CHSHEvaluator,
    GroverWeakDisturbanceAmplifier,
    CrossVerifierConsensusEngine,
    StatisticalThreatDetector
)


class ThreatDetectionService:
    """Service layer for non-AI statistical threat detection."""

    def __init__(self):
        self.detector = StatisticalThreatDetector()

    def evaluate_chsh(self, num_pairs: int = 100, channel_depolarizing: float = 0.0, is_entangled: bool = True) -> Dict[str, Any]:
        """Runs CHSH inequality evaluation."""
        return CHSHEvaluator.simulate_chsh_test(
            num_pairs=num_pairs,
            channel_depolarizing=channel_depolarizing,
            is_entangled=is_entangled
        )

    def evaluate_grover_amplification(self, raw_qber: float, num_iterations: int = 2) -> Dict[str, Any]:
        """Applies Grover-inspired weak disturbance amplification."""
        return GroverWeakDisturbanceAmplifier.amplify_disturbance(
            raw_qber=raw_qber,
            num_iterations=num_iterations
        )

    def evaluate_cross_verifier_consensus(self,
                                          states_bob: Optional[List] = None,
                                          states_charlie: Optional[List] = None,
                                          is_repudiation: bool = False) -> Dict[str, Any]:
        """Evaluates non-repudiation between Bob and Charlie."""
        if states_bob is None or states_charlie is None:
            # Generate representative states for verification
            from core.qds_teleport_core import STATE_0, STATE_1
            if not is_repudiation:
                states_bob = [np.outer(STATE_0, np.conj(STATE_0)) for _ in range(16)]
                states_charlie = [np.outer(STATE_0, np.conj(STATE_0)) for _ in range(16)]
            else:
                states_bob = [np.outer(STATE_0, np.conj(STATE_0)) for _ in range(16)]
                states_charlie = [np.outer(STATE_1, np.conj(STATE_1)) for _ in range(16)]
        return CrossVerifierConsensusEngine.evaluate_consensus(
            states_bob=states_bob,
            states_charlie=states_charlie,
            is_repudiation_attack=is_repudiation
        )

    def compute_bounds(self, L: int, pe: float = 0.01) -> Dict[str, Any]:
        """Calculates verification and security thresholds based on Chernoff bounds."""
        tv = self.detector.calculate_verification_threshold(L, pe)
        tf = self.detector.calculate_forgery_threshold(L, pe)
        p_forge = self.detector.calculate_theoretical_p_forge(L)
        p_scipy = self.detector.calculate_exact_scipy_p_forge(L)
        return {
            "key_length": L,
            "verification_threshold_Tv": tv,
            "forgery_threshold_Tf": tf,
            "theoretical_p_forge": p_forge,
            "scipy_exact_p_forge": p_scipy
        }
