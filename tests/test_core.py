import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from core.qds_teleport_core import KeyGenerator, QuantumTeleportationEngine, EIGENSTATE_MAP

def test_teleportation():
    print("Testing Teleportation of all 6 Pauli eigenstates...")
    for (basis, val), state in EIGENSTATE_MAP.items():
        c, rho_rec, info = QuantumTeleportationEngine.teleport_single_qubit(state, channel_noise_level=0.0)
        fidelity = float(np.real(np.vdot(state, rho_rec @ state)))
        purity = info["purity"]
        print(f"Basis {basis}, Val {val:+d} -> Bell outcome {c} -> Fidelity: {fidelity:.6f}, Purity: {purity:.6f}")
        assert np.isclose(fidelity, 1.0, atol=1e-5), f"Fidelity failure for {basis}, {val}"
    print(">>> ALL 6 PAULI EIGENSTATES TELEPORT WITH 100% FIDELITY DETERMINISTICALLY! <<<")

if __name__ == "__main__":
    test_teleportation()
