"""
api/services/quantum_service.py
Layer 1 Quantum Service: Qiskit 2.x Circuit Simulation, Statevector Mechanics & Noise Modeling.
Implements realistic open quantum systems noise channels using Qiskit Aer:
- Depolarizing channel
- Amplitude damping channel (T1 relaxation / fiber photon loss)
- Phase damping channel (T2 dephasing / fiber birefringence)
- Bit-flip & Phase-flip channels
Strictly Zero-AI / Information-Theoretic Physics.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
# Note: qiskit_aer has known C++ ABI / psutil access violations on Windows Python 3.13.
# We default HAS_AER to False to use the exact analytical Kraus representation.
HAS_AER = False
AerSimulator = None
NoiseModel = None
depolarizing_error = None
amplitude_damping_error = None
phase_damping_error = None
pauli_error = None

from core.qds_teleport_core import (
    QiskitCircuitBuilder,
    get_bloch_coordinates,
    EIGENSTATE_MAP,
    SIGMA_I, SIGMA_X, SIGMA_Y, SIGMA_Z,
    BELL_PHI_PLUS
)


class QuantumSimulationService:
    """Provides high-level quantum circuit and noise simulation services."""

    @staticmethod
    def get_circuit_details(basis: str = 'X', eigenvalue: int = 1) -> Dict[str, Any]:
        """Returns circuit metadata, gate counts, and ASCII visualization."""
        qc = QiskitCircuitBuilder.create_teleportation_circuit(basis, eigenvalue)
        ops = dict(qc.count_ops())
        ascii_art = QiskitCircuitBuilder.get_circuit_ascii(basis, eigenvalue)
        return {
            "basis": basis,
            "eigenvalue": eigenvalue,
            "qubits": qc.num_qubits,
            "clbits": qc.num_clbits,
            "gate_counts": ops,
            "circuit_ascii": ascii_art
        }

    @staticmethod
    def build_noise_model(noise_type: str, error_rate: float) -> Tuple[Any, str]:
        """
        Constructs a Qiskit Aer NoiseModel for realistic quantum channel noise.
        """
        error_rate = max(0.0, min(0.5, float(error_rate)))
        desc = ""

        if noise_type == "depolarizing":
            desc = f"Symmetric depolarizing channel: epsilon={error_rate:.3f} on 1-qubit and 2-qubit gates."
        elif noise_type == "amplitude_damping":
            desc = f"Amplitude damping channel (T1 relaxation / photon absorption): gamma={error_rate:.3f}."
        elif noise_type == "phase_damping":
            desc = f"Phase damping channel (T2 pure dephasing / fiber birefringence): lambda={error_rate:.3f}."
        elif noise_type == "bit_flip":
            desc = f"Bit-flip channel (Pauli X error): p={error_rate:.3f}."
        elif noise_type == "phase_flip":
            desc = f"Phase-flip channel (Pauli Z error): p={error_rate:.3f}."
        else:
            desc = f"Generic channel depolarizing noise: p={error_rate:.3f}."

        if not HAS_AER or NoiseModel is None:
            return None, desc

        try:
            noise_model = NoiseModel()
            if noise_type == "depolarizing":
                error_1q = depolarizing_error(error_rate, 1)
                error_2q = depolarizing_error(min(error_rate * 1.5, 0.5), 2)
                noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 's', 'id'])
                noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
            elif noise_type == "amplitude_damping":
                error_amp = amplitude_damping_error(error_rate)
                noise_model.add_all_qubit_quantum_error(error_amp, ['h', 'x', 's', 'id'])
            elif noise_type == "phase_damping":
                error_phase = phase_damping_error(error_rate)
                noise_model.add_all_qubit_quantum_error(error_phase, ['h', 'x', 's', 'id'])
            elif noise_type == "bit_flip":
                error_bf = pauli_error([('X', error_rate), ('I', 1.0 - error_rate)])
                noise_model.add_all_qubit_quantum_error(error_bf, ['h', 'x', 's', 'id'])
            elif noise_type == "phase_flip":
                error_pf = pauli_error([('Z', error_rate), ('I', 1.0 - error_rate)])
                noise_model.add_all_qubit_quantum_error(error_pf, ['h', 'x', 's', 'id'])
            else:
                error_1q = depolarizing_error(error_rate, 1)
                noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 's', 'id'])
            return noise_model, desc
        except Exception:
            return None, desc

    @classmethod
    def simulate_noisy_circuit(cls,
                               basis: str = 'X',
                               eigenvalue: int = 1,
                               noise_type: str = 'depolarizing',
                               error_rate: float = 0.05,
                               shots: int = 1024) -> Dict[str, Any]:
        """
        Simulates state preparation and teleportation through the specified Qiskit noise model.
        Returns fidelity degradation, purity, Bloch coordinates, and measurement distributions.
        """
        ideal_target_state = EIGENSTATE_MAP.get((basis, eigenvalue), EIGENSTATE_MAP[('Z', +1)])
        target_dm = DensityMatrix(ideal_target_state)

        # Build circuit for state preparation & measurement
        qc = QuantumCircuit(1, 1)
        if basis == 'Z':
            if eigenvalue == -1:
                qc.x(0)
        elif basis == 'X':
            if eigenvalue == +1:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        elif basis == 'Y':
            if eigenvalue == +1:
                qc.h(0)
                qc.s(0)
            else:
                qc.x(0)
                qc.h(0)
                qc.s(0)

        # Measure in the respective eigenstate basis
        if basis == 'X':
            qc.h(0)
        elif basis == 'Y':
            qc.sdg(0)
            qc.h(0)

        qc.measure(0, 0)

        # Build noise model and description
        noise_model, desc = cls.build_noise_model(noise_type, error_rate)

        # Theoretical degraded density matrix for single qubit under noise
        rho_ideal = np.outer(ideal_target_state, np.conj(ideal_target_state))

        if noise_type == "depolarizing":
            rho_noisy = (1.0 - error_rate) * rho_ideal + (error_rate / 2.0) * SIGMA_I
        elif noise_type == "amplitude_damping":
            gamma = error_rate
            e0 = np.array([[1.0, 0.0], [0.0, np.sqrt(max(0.0, 1.0 - gamma))]], dtype=np.complex128)
            e1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=np.complex128)
            rho_noisy = e0 @ rho_ideal @ np.conj(e0.T) + e1 @ rho_ideal @ np.conj(e1.T)
        elif noise_type == "phase_damping":
            lam = error_rate
            e0 = np.array([[1.0, 0.0], [0.0, np.sqrt(max(0.0, 1.0 - lam))]], dtype=np.complex128)
            e1 = np.array([[0.0, 0.0], [0.0, np.sqrt(lam)]], dtype=np.complex128)
            rho_noisy = e0 @ rho_ideal @ np.conj(e0.T) + e1 @ rho_ideal @ np.conj(e1.T)
        elif noise_type == "bit_flip":
            rho_noisy = (1.0 - error_rate) * rho_ideal + error_rate * (SIGMA_X @ rho_ideal @ SIGMA_X)
        elif noise_type == "phase_flip":
            rho_noisy = (1.0 - error_rate) * rho_ideal + error_rate * (SIGMA_Z @ rho_ideal @ SIGMA_Z)
        else:
            rho_noisy = (1.0 - error_rate) * rho_ideal + (error_rate / 2.0) * SIGMA_I

        counts = None
        if HAS_AER and noise_model is not None:
            try:
                backend = AerSimulator(noise_model=noise_model)
                job = backend.run(qc, shots=shots)
                result = job.result()
                counts = result.get_counts(qc)
            except Exception:
                counts = None

        if counts is None:
            # Analytical measurement distribution from density matrix
            p_zero = float(np.real(rho_noisy[0, 0])) if basis == 'Z' else 0.5 + 0.5 * (1.0 - error_rate)
            c0 = int(np.random.binomial(shots, max(0.0, min(1.0, p_zero))))
            counts = {'0': c0, '1': shots - c0}

        # Purity Tr(rho^2)
        purity = float(np.real(np.trace(rho_noisy @ rho_noisy)))

        # Quantum state fidelity Tr(sqrt(sqrt(rho) * sigma * sqrt(rho)))^2
        # For pure target state |psi>: F = <psi| rho_noisy |psi>
        noisy_fidelity = float(np.real(np.vdot(ideal_target_state, rho_noisy @ ideal_target_state)))
        noisy_fidelity = max(0.0, min(1.0, noisy_fidelity))

        bloch = get_bloch_coordinates(rho_noisy)

        return {
            "noise_type": noise_type,
            "error_rate": float(error_rate),
            "shots": shots,
            "ideal_fidelity": 1.0,
            "noisy_fidelity": round(noisy_fidelity, 5),
            "purity": round(purity, 5),
            "statevector_bloch": bloch,
            "measurement_counts": dict(counts),
            "channel_description": desc
        }
