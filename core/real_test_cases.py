"""
core/real_test_cases.py
Realistic Structured Test Case Library for QuantumGuard QDS.
Replaces simplistic placeholder strings with real-world enterprise, financial,
critical infrastructure, blockchain, and aerospace cryptographic payloads.

Includes:
1. SWIFT MT103 / ISO 20022 High-Value Interbank Wire Transfer
2. Ethereum EIP-712 Structured Smart Contract Transaction
3. SCADA IEC 60870-5-104 / DNP3 High-Voltage Grid Switching Command
4. CCSDS Satellite / Drone Telecommand Guidance Packet
5. HL7 FHIR DEA Schedule II Critical Medical Prescription
6. Multi-Party JWT Bearer Authorization Token

Supports real-world field-level adversarial tampering (e.g., modifying beneficiary IBAN,
re-routing power grid busbars, spoofing satellite coordinates).
"""

import json
import hashlib
import time
from typing import Dict, Any, Tuple, List, Optional


REAL_TEST_CASE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "SWIFT_WIRE_TRANSFER": {
        "id": "SWIFT_WIRE_TRANSFER",
        "name": "SWIFT MT103 / ISO 20022 Cross-Border Wire Transfer",
        "category": "Financial & Banking",
        "standard": "ISO 20022 / SWIFT MT103",
        "description": "High-value $10,000,000 interbank fund transfer between commercial banks.",
        "payload": {
            "transaction_id": "TXN-2026-CH-99482104",
            "message_type": "pacs.008.001.08",
            "uetr": "eb3d8b2f-9a11-4712-88ec-d7301cfa9901",
            "sender": {
                "institution": "UBS Switzerland AG",
                "bic": "UBSWCHZHXXX",
                "account_iban": "CH9300240240123456789",
                "authorized_officer": "Alice M. Vontobel"
            },
            "beneficiary": {
                "institution": "JPMorgan Chase Bank N.A.",
                "bic": "CHASUS33XXX",
                "account_iban": "US64CHAS1234567890123456",
                "name": "Acme Global Technology Corp"
            },
            "transfer_amount": {
                "value": 10000000.00,
                "currency": "USD",
                "settlement_date": "2026-10-23"
            },
            "purpose_code": "INTC - Intra-Company Treasury Settlement",
            "audit_compliance_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
        "tamper_options": {
            "field": "beneficiary.account_iban",
            "tampered_value": "RU8902000000000000000",
            "amount_inflation": 50000000.00,
            "attack_narrative": "Adversary performs Man-in-the-Middle wire manipulation, redirecting $50M to an unauthorized offshore account."
        }
    },

    "EIP712_SMART_CONTRACT": {
        "id": "EIP712_SMART_CONTRACT",
        "name": "Ethereum EIP-712 Typed Smart Contract Execution",
        "category": "Blockchain & Web3",
        "standard": "ERC-712 / EVM ABI",
        "description": "Multi-sig DAO treasury disbursement transaction authorizing token release.",
        "payload": {
            "domain": {
                "name": "QuantumVault Treasury",
                "version": "2.0.0",
                "chainId": 1,
                "verifyingContract": "0x1a9C8182C09F50C8318d769245beA52c32BE35BC"
            },
            "primaryType": "PermitTransferFrom",
            "message": {
                "permitted": {
                    "token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "amount": "2500000000000"
                },
                "spender": "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD",
                "nonce": 4210,
                "deadline": 1792684800,
                "recipient": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
            }
        },
        "tamper_options": {
            "field": "message.recipient",
            "tampered_value": "0x000000000000000000000000000000000000dEaD",
            "attack_narrative": "Smart contract front-runner intercepts transaction payload and rewrites recipient address to attacker contract."
        }
    },

    "SCADA_GRID_SWITCHING": {
        "id": "SCADA_GRID_SWITCHING",
        "name": "SCADA IEC 60870-5-104 High-Voltage Grid Switching",
        "category": "Critical Infrastructure",
        "standard": "IEC 60870-5-104 / DNP3",
        "description": "High-voltage 400kV power substation remote breaker disconnect command.",
        "payload": {
            "asdu_address": 104,
            "information_object_address": 4012,
            "substation_id": "SUB-NORTH-GRID-400KV",
            "equipment_id": "BREAKER-CB-401A",
            "command": "OPEN_CIRCUIT_BREAKER",
            "quarantine_interlock_active": True,
            "priority": "LEVEL_1_CRITICAL",
            "execution_window_ms": 500,
            "operator_credential_cert": "CERT-GRID-OPS-2026-PRIMARY",
            "telemetry_checksum_crc32": "0xA94F12E0"
        },
        "tamper_options": {
            "field": "command",
            "tampered_value": "OVERRIDE_AND_TRIP_ALL_FEEDERS_BLACKOUT",
            "attack_narrative": "Cyber warfare APT injects malicious grid command to force cascading blackout across regional transmission network."
        }
    },

    "CCSDS_SATELLITE_TELECOMMAND": {
        "id": "CCSDS_SATELLITE_TELECOMMAND",
        "name": "CCSDS Spacecraft Orbit Trajectory & Telecommand",
        "category": "Aerospace & Defense",
        "standard": "CCSDS 232.0-B-4 TC Packet",
        "description": "Defense communication satellite orbital thruster delta-V burn command packet.",
        "payload": {
            "spacecraft_norad_id": 58214,
            "subsystem": "PROPULSION_ATTITUDE_CONTROL",
            "apid": "0x01A4",
            "sequence_count": 94812,
            "thruster_firing_vector": {
                "delta_vx_mps": 0.452,
                "delta_vy_mps": -0.118,
                "delta_vz_mps": 1.294,
                "duration_seconds": 14.80
            },
            "target_orbital_slot": "GEO-104.2E",
            "anti_spoofing_token": "QDS-SAT-TOKEN-88319-VERIFIED"
        },
        "tamper_options": {
            "field": "thruster_firing_vector.delta_vz_mps",
            "tampered_value": -85.000,
            "attack_narrative": "Adversarial ground station spoofs delta-V thruster vector to destabilize orbit into atmospheric decay trajectory."
        }
    },

    "HL7_FHIR_MEDICAL": {
        "id": "HL7_FHIR_MEDICAL",
        "name": "HL7 FHIR DEA Schedule II Critical Prescription",
        "category": "Healthcare & Identity",
        "standard": "HL7 FHIR R4 MedicationRequest",
        "description": "Physician-authenticated controlled substance prescription with DEA digital certificate.",
        "payload": {
            "resourceType": "MedicationRequest",
            "id": "rx-2026-fentanyl-transdermal",
            "status": "active",
            "intent": "order",
            "medication": {
                "drug_name": "Fentanyl Transdermal System",
                "dea_schedule": "SCHEDULE_II",
                "dose_quantity_mcg": 25,
                "frequency": "Every 72 hours"
            },
            "patient": {
                "national_id": "PT-US-9912048-A",
                "name": "Robert J. Hawkins",
                "dob": "1968-04-12"
            },
            "prescriber": {
                "npi": "1942084920",
                "dea_reg_number": "BM9481204",
                "physician_name": "Dr. Sarah Lin, MD (Oncology)"
            }
        },
        "tamper_options": {
            "field": "medication.dose_quantity_mcg",
            "tampered_value": 2500,
            "attack_narrative": "Malicious pharmacy terminal tampers with DEA Schedule II dosage by 100x lethal concentration."
        }
    },

    "JWT_OAUTH2_AUTH": {
        "id": "JWT_OAUTH2_AUTH",
        "name": "Multi-Party Cryptographic JWT API Access Token",
        "category": "Enterprise Security",
        "standard": "RFC 7519 / OIDC Core",
        "description": "Zero-trust microservice federation authorization claims token.",
        "payload": {
            "header": {
                "alg": "QDS-TELEPORT-SHA256",
                "typ": "JWT",
                "kid": "key-sec-auth-2026"
            },
            "claims": {
                "iss": "https://auth.quantumguard.internal",
                "sub": "service-worker-7729",
                "aud": "core-banking-ledger-api",
                "role": "auditor_read_only",
                "scope": ["read:telemetry", "verify:ledger"],
                "exp": 1792688400,
                "nbf": 1761152400
            }
        },
        "tamper_options": {
            "field": "claims.role",
            "tampered_value": "superadmin_full_system_write_privilege",
            "attack_narrative": "Privilege escalation: adversary elevates bearer token claims from read_only auditor to superadmin root."
        }
    }
}


class RealTestCaseService:
    """Provides real-world structured payloads, canonical hashing, and payload tampering."""

    @classmethod
    def list_test_cases(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all available real-world test cases."""
        items = []
        for case_id, case_data in REAL_TEST_CASE_REGISTRY.items():
            items.append({
                "id": case_id,
                "name": case_data["name"],
                "category": case_data["category"],
                "standard": case_data["standard"],
                "description": case_data["description"],
                "tamper_narrative": case_data["tamper_options"]["attack_narrative"]
            })
        return items

    @classmethod
    def get_test_case(cls, case_id: str) -> Optional[Dict[str, Any]]:
        """Fetches full payload structure and tamper options for a specific test case."""
        return REAL_TEST_CASE_REGISTRY.get(case_id)

    @classmethod
    def canonicalize_payload(cls, payload: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generates deterministic JSON serialization and SHA-256 cryptographic digest.
        Ensures consistent, reproducible quantum digital signature key mapping.
        """
        canonical_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        return canonical_str, digest

    @classmethod
    def prepare_test_case_payload(cls,
                                  case_id: str,
                                  apply_tampering: bool = False) -> Dict[str, Any]:
        """
        Prepares a test case for signing and verification.
        If apply_tampering is True, modifies the exact payload fields as specified in tamper_options.
        """
        case = cls.get_test_case(case_id)
        if case is None:
            # Fallback for generic payload
            case = REAL_TEST_CASE_REGISTRY["SWIFT_WIRE_TRANSFER"]

        original_payload = json.loads(json.dumps(case["payload"]))
        tampered_payload = json.loads(json.dumps(case["payload"]))
        tamper_details = {}

        if apply_tampering:
            opts = case["tamper_options"]
            field_path = opts["field"].split('.')
            target = tampered_payload
            for part in field_path[:-1]:
                target = target[part]
            original_val = target[field_path[-1]]
            target[field_path[-1]] = opts["tampered_value"]

            # If amount inflation option exists, update amount as well
            if "amount_inflation" in opts and "transfer_amount" in tampered_payload:
                tampered_payload["transfer_amount"]["value"] = opts["amount_inflation"]

            tamper_details = {
                "tampered": True,
                "target_field": opts["field"],
                "original_value": original_val,
                "tampered_value": opts["tampered_value"],
                "attack_narrative": opts["attack_narrative"]
            }
        else:
            tamper_details = {
                "tampered": False,
                "attack_narrative": "Legitimate, uncompromised transaction payload."
            }

        orig_str, orig_digest = cls.canonicalize_payload(original_payload)
        tamp_str, tamp_digest = cls.canonicalize_payload(tampered_payload)

        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "category": case["category"],
            "standard": case["standard"],
            "original_payload": original_payload,
            "original_digest": orig_digest,
            "active_payload": tampered_payload if apply_tampering else original_payload,
            "active_canonical_str": tamp_str if apply_tampering else orig_str,
            "active_digest": tamp_digest if apply_tampering else orig_digest,
            "tamper_info": tamper_details
        }
