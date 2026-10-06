"""
qds_teleport_core.py
Deliverable D1: Quantum Teleportation & QDS Simulation Engine
Ground Truth Implementation based on SIH Problem Statement ID 26141 & Specification Documents 3 and 4.
Combines Qiskit 2.x Quantum Circuit Statevector Simulation with High-Speed NumPy Linear Algebra.
Strictly Zero-AI / Information-Theoretic Quantum Mechanics.
"""

import secrets
import numpy as np
from typing import Tuple, List, Dict, Any, Optional

# Qiskit 2.x Imports
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity

# Pauli Matrices (NumPy)
SIGMA_I = np.array([[1.0 + 0.0j, 0.0 + 0.0j],
                    [0.0 + 0.0j, 1.0 + 0.0j]], dtype=np.complex128)

SIGMA_X = np.array([[0.0 + 0.0j, 1.0 + 0.0j],
                    [1.0 + 0.0j, 0.0 + 0.0j]], dtype=np.complex128)

SIGMA_Y = np.array([[0.0 + 0.0j, -1.0j],
                    [1.0j, 0.0 + 0.0j]], dtype=np.complex128)

SIGMA_Z = np.array([[1.0 + 0.0j, 0.0 + 0.0j],
                    [0.0 + 0.0j, -1.0 + 0.0j]], dtype=np.complex128)

# 6 Pauli Eigenstates:
# sigma_z: |0>, |1>
# sigma_x: |+>, |->
# sigma_y: |+i>, |-i>
STATE_0 = np.array([1.0 + 0.0j, 0.0 + 0.0j], dtype=np.complex128)
STATE_1 = np.array([0.0 + 0.0j, 1.0 + 0.0j], dtype=np.complex128)

STATE_PLUS = (STATE_0 + STATE_1) / np.sqrt(2.0)
STATE_MINUS = (STATE_0 - STATE_1) / np.sqrt(2.0)

STATE_PLUS_I = (STATE_0 + 1.0j * STATE_1) / np.sqrt(2.0)
STATE_MINUS_I = (STATE_0 - 1.0j * STATE_1) / np.sqrt(2.0)

# Pauli Eigenstate Map: (basis, eigenvalue) -> state_vector
EIGENSTATE_MAP = {
    ('Z', +1): STATE_0,
    ('Z', -1): STATE_1,
    ('X', +1): STATE_PLUS,
    ('X', -1): STATE_MINUS,
    ('Y', +1): STATE_PLUS_I,
    ('Y', -1): STATE_MINUS_I,
}

# Standard Bell states for 2 qubits (basis: |00>, |01>, |10>, |11>)
BELL_PHI_PLUS = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128) / np.sqrt(2.0)
BELL_PHI_MINUS = np.array([1.0, 0.0, 0.0, -1.0], dtype=np.complex128) / np.sqrt(2.0)
BELL_PSI_PLUS = np.array([0.0, 1.0, 1.0, 0.0], dtype=np.complex128) / np.sqrt(2.0)
BELL_PSI_MINUS = np.array([0.0, 1.0, -1.0, 0.0], dtype=np.complex128) / np.sqrt(2.0)

BELL_BASIS = [BELL_PHI_PLUS, BELL_PHI_MINUS, BELL_PSI_PLUS, BELL_PSI_MINUS]
BELL_OUTCOMES = ['00', '01', '10', '11']


def get_bloch_coordinates(state_vector_or_density) -> Dict[str, float]:
    """Computes (x, y, z) Bloch sphere coordinates from a statevector or density matrix."""
    if isinstance(state_vector_or_density, np.ndarray):
        if state_vector_or_density.ndim == 1:
            rho = np.outer(state_vector_or_density, np.conj(state_vector_or_density))
        else:
            rho = state_vector_or_density
    elif hasattr(state_vector_or_density, "data"):
        data = state_vector_or_density.data
        if data.ndim == 1:
            rho = np.outer(data, np.conj(data))
        else:
            rho = data
    else:
        rho = np.array(state_vector_or_density)

    x = float(np.real(np.trace(rho @ SIGMA_X)))
    y = float(np.real(np.trace(rho @ SIGMA_Y)))
    z = float(np.real(np.trace(rho @ SIGMA_Z)))
    return {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)}


def get_pauli_correction(c: str) -> np.ndarray:
    """
    Computes Bob's Pauli correction unitary U_Pauli(c) = (sigma_x)^c1 * (sigma_z)^c2
    c = '00' -> I
    c = '01' -> sigma_z
    c = '10' -> sigma_x
    c = '11' -> sigma_x @ sigma_z = -i * sigma_y
    """
    if c == '00':
        return SIGMA_I
    elif c == '01':
        return SIGMA_Z
    elif c == '10':
        return SIGMA_X
    elif c == '11':
        return SIGMA_X @ SIGMA_Z
    else:
        raise ValueError(f"Invalid Bell measurement outcome: {c}")


class QiskitCircuitBuilder:
    """Builds and simulates authentic Qiskit Quantum Circuits for teleportation and Bell pairs."""

    @staticmethod
    def create_teleportation_circuit(basis: str, eigenvalue: int) -> QuantumCircuit:
        """
        Constructs a 3-qubit Qiskit QuantumCircuit:
        Qubit 0 (S): Alice's secret Pauli eigenstate state
        Qubit 1 (A): Alice's half of entangled Bell pair
        Qubit 2 (B): Bob's half of entangled Bell pair
        """
        qc = QuantumCircuit(3, 2, name="QDS_Teleportation")

        # Step 1: Prepare secret Pauli eigenstate on Qubit 0
        if basis == 'Z':
            if eigenvalue == -1:
                qc.x(0)  # |1>
        elif basis == 'X':
            if eigenvalue == +1:
                qc.h(0)  # |+>
            else:
                qc.x(0)
                qc.h(0)  # |->
        elif basis == 'Y':
            if eigenvalue == +1:
                qc.h(0)
                qc.s(0)  # |+i>
            else:
                qc.x(0)
                qc.h(0)
                qc.s(0)  # |-i>
        qc.barrier(label="Prep")

        # Step 2: Create EPR Bell Pair between Qubits 1 and 2: |Phi+> = 1/sqrt(2)(|00> + |11>)
        qc.h(1)
        qc.cx(1, 2)
        qc.barrier(label="Bell_Pair")

        # Step 3: Alice's Joint Bell-Basis Measurement on Qubits (0, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.barrier(label="Alice_Bell_Proj")

        qc.measure(0, 0)
        qc.measure(1, 1)

        # Step 4: Bob's Unitary Pauli Corrections on Qubit 2
        # If bit 1 == 1, apply X; If bit 0 == 1, apply Z
        # In Qiskit 2.x, conditional gates or dynamic circuit operations
        return qc

    @staticmethod
    def get_circuit_ascii(basis: str = 'X', eigenvalue: int = 1) -> str:
        """Returns ASCII representation of the Qiskit teleportation circuit."""
        qc = QiskitCircuitBuilder.create_teleportation_circuit(basis, eigenvalue)
        return str(qc.draw(output='text'))


class KeyGenerator:
    """Phase 1: CSPRNG Secret Key Generation & Pauli Eigenstate Preparation."""

    @staticmethod
    def generate_keys_for_bit(L: int) -> Tuple[List[str], List[int]]:
        """
        Generates basis key B_b in {'X', 'Y', 'Z'}^L
        and eigenvalue key V_b in {+1, -1}^L using CSPRNG (secrets).
        """
        bases = ['X', 'Y', 'Z']
        eigenvalues = [+1, -1]

        basis_key = [secrets.choice(bases) for _ in range(L)]
        eigenvalue_key = [secrets.choice(eigenvalues) for _ in range(L)]
        return basis_key, eigenvalue_key

    @staticmethod
    def prepare_quantum_states(basis_key: List[str], eigenvalue_key: List[int]) -> List[np.ndarray]:
        """Maps (B_b, V_b) pairs to the 6-state Pauli alphabet."""
        states = []
        for b, v in zip(basis_key, eigenvalue_key):
            states.append(EIGENSTATE_MAP[(b, v)].copy())
        return states


class QuantumTeleportationEngine:
    """Phase 2 & 3: Bell State Entanglement & Quantum Teleportation Channel."""

    @staticmethod
    def teleport_single_qubit(state_s: np.ndarray,
                              channel_noise_level: float = 0.0) -> Tuple[str, np.ndarray, Dict[str, Any]]:
        """
        Executes genuine 3-qubit quantum teleportation:
        Initial state: |psi>_S (x) |Phi+>_AB = (alpha|0> + beta|1>) (x) 1/sqrt(2)(|00> + |11>)
        Alice performs joint Bell-basis projection on particles (S, A).
        Outcome c in {'00', '01', '10', '11'} obtained with probability 1/4 each.
        Bob applies U_Pauli(c) to reconstruct |psi>_S on particle B.
        """
        # Form 3-qubit state: |psi>_S (x) |Phi+>_AB
        psi_3q = np.kron(state_s, BELL_PHI_PLUS)

        probabilities = []
        post_measurement_states_3q = []

        for k in range(4):
            bell_k = BELL_BASIS[k]
            P_SA = np.outer(bell_k, np.conj(bell_k))
            P_3q = np.kron(P_SA, SIGMA_I)

            projected = P_3q @ psi_3q
            prob = float(np.real(np.vdot(projected, projected)))
            probabilities.append(prob)
            norm = np.linalg.norm(projected)
            if norm > 1e-12:
                post_measurement_states_3q.append(projected / norm)
            else:
                post_measurement_states_3q.append(projected)

        probabilities = np.array(probabilities)
        prob_sum = np.sum(probabilities)
        if prob_sum > 0:
            probabilities = probabilities / prob_sum
        else:
            probabilities = np.array([0.25, 0.25, 0.25, 0.25])

        chosen_idx = int(np.random.choice(4, p=probabilities))
        c = BELL_OUTCOMES[chosen_idx]
        post_state = post_measurement_states_3q[chosen_idx]

        # Partial trace over qubits S and A to extract Bob's qubit B
        tensor_state = post_state.reshape((2, 2, 2))
        rho_3q = np.tensordot(tensor_state, np.conj(tensor_state), axes=0)
        rho_B = np.trace(np.trace(rho_3q, axis1=0, axis2=3), axis1=0, axis2=2)

        # Bob applies Pauli correction unitary
        u_correction = get_pauli_correction(c)
        rho_reconstructed = u_correction @ rho_B @ np.conj(u_correction.T)

        # Apply optical depolarizing noise if present
        if channel_noise_level > 0.0:
            rho_reconstructed = (1.0 - channel_noise_level) * rho_reconstructed + (channel_noise_level / 2.0) * SIGMA_I

        purity = float(np.real(np.trace(rho_reconstructed @ rho_reconstructed)))

        teleport_info = {
            "bell_outcome": c,
            "correction_applied": f"U_Pauli({c})",
            "purity": round(purity, 4),
            "bloch_reconstructed": get_bloch_coordinates(rho_reconstructed)
        }
        return c, rho_reconstructed, teleport_info
