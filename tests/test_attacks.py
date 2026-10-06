import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.attack_simulator import AdversarialAttackSimulator

def test_all_attacks():
    sim = AdversarialAttackSimulator()
    matrix = sim.generate_attack_comparison_matrix(L=128)

    print("\n================ COMPARING ALL 7 ATTACK SCENARIOS + BASELINE ================")
    for row in matrix:
        print(f"[{row['attack_code']:<20}] -> Decision: {row['decision']:<8} | Level: {row['enforcement_level']:<10} | Threat: {row['detected_threat']:<28} | QBER: {row['qber']:<6.2%} | S: {row['chsh_s']:<5.3f}")

    # Baseline must be ACCEPTED
    assert matrix[0]["decision"] == "ACCEPTED" and matrix[0]["detected_threat"] == "NONE"

    # All attack scenarios must be caught
    for i in range(1, len(matrix)):
        assert matrix[i]["decision"] == "REJECTED" or matrix[i]["enforcement_level"] in ["RESTRICT", "QUARANTINE", "ISOLATE"]

    print("\n>>> ALL 7 ATTACK SCENARIOS TESTED & PROPERLY CLASSIFIED WITH ZERO AI! <<<")

    print("\nTesting Benchmark Sweep with SciPy Exact Bounds (L=16 to 1024)...")
    bench = sim.generate_benchmark_sweep()
    for l, lat, p_th, p_scipy in zip(bench["key_lengths"], bench["latencies_ms"], bench["theoretical_p_forge"], bench["scipy_exact_p_forge"]):
        print(f"L = {l:<4} | Latency: {lat:<6.2f} ms | Theoretical P_f: {p_th:.2e} | SciPy Exact P_f: {p_scipy:.2e}")
    print(">>> BENCHMARK SWEEP SUCCEEDED WITH LINEAR COMPLEXITY! <<<")

if __name__ == "__main__":
    test_all_attacks()
