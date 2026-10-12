import numpy as np
from core.attack_simulator import AdversarialAttackSimulator
from core.threat_detector_stat import StatisticalThreatDetector, CHSHEvaluator
from core.qds_teleport_core import *

sim = AdversarialAttackSimulator()

print("=" * 90)
print("NOISE SWEEP TEST: LEGITIMATE (NONE) WITH VARYING CHANNEL NOISE")
print("=" * 90)
for n in [0.0, 0.02, 0.05, 0.08, 0.10, 0.11, 0.12, 0.13, 0.15, 0.18, 0.20, 0.25]:
    r = sim.run_pipeline('Test message', L=128, attack_type='NONE', channel_noise=n)
    q = r['qber_analysis']
    c = r['chsh']
    d = r['decision']
    print(f"Noise: {n*100:4.1f}% | QBER: {q['qber']*100:5.2f}% | S: {c['S_value']:5.3f} | Delta_E: {q['basis_asymmetry']*100:4.1f}% | Level: {d['enforcement_level']:10s} | Dec: {d['decision']:8s} | Threat: {d['threat_type']}")

print("\n" + "=" * 90)
print("ALL 7 ATTACK SCENARIOS AT BASELINE NOISE (0.01)")
print("=" * 90)
for atk in ["NONE", "FORGERY", "IMPERSONATION", "INTERCEPT_RESEND", "REPLAY", "UNAUTHORIZED_PROBE", "WEAK_INTERCEPT", "REPUDIATION"]:
    r = sim.run_pipeline('Test message', L=128, attack_type=atk, channel_noise=0.01)
    q = r['qber_analysis']
    c = r['chsh']
    d = r['decision']
    print(f"Attack: {atk:18s} | QBER: {q['qber']*100:5.2f}% | S: {c['S_value']:5.3f} | Delta_E: {q['basis_asymmetry']*100:4.1f}% | Level: {d['enforcement_level']:10s} | Threat: {d['threat_type']}")
