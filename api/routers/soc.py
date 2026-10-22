"""
api/routers/soc.py
FastAPI router for Enterprise SOC / SIEM Integration, ArcSight CEF Streams,
MITRE ATT&CK STIX 2.1 Threat Intelligence, and Automated Zero-Trust Firewall Playbooks.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.cybersecurity_soc import SHARED_SOC_ENGINE
from core.adversarial_engine import ATTACK_PROFILES_METADATA

router = APIRouter(tags=["soc"])


class FirewallPlaybookRequest(BaseModel):
    session_id: str = Field(default="SESS-INCIDENT-9912")
    threat_type: str = Field(default="QUANTUM_MITM_EAVESDROPPING")
    enforcement_level: str = Field(default="ISOLATE")
    adversary_ip: str = Field(default="198.51.100.77")
    affected_optical_port: str = Field(default="TenGigE0/1/0/4")


@router.get("/api/soc/cef-stream")
def get_cef_telemetry(session_id: str = Query("SESS-TELEMETRY-8821"),
                      threat_type: str = Query("QUANTUM_MITM_EAVESDROPPING"),
                      enforcement_level: str = Query("ISOLATE"),
                      qber: float = Query(0.25),
                      chsh_s: float = Query(2.012),
                      mitre_id: str = Query("T1557.002")) -> Dict[str, Any]:
    """
    Returns RFC 5424 Syslog stream formatted in ArcSight Common Event Format (CEF)
    ready for ingestion by Splunk, Elastic SIEM, Microsoft Sentinel, or IBM QRadar.
    """
    cef_string = SHARED_SOC_ENGINE.format_cef_event(
        session_id=session_id,
        threat_type=threat_type,
        enforcement_level=enforcement_level,
        qber=qber,
        chsh_s=chsh_s,
        mitre_technique_id=mitre_id
    )
    return {
        "format": "ArcSight Common Event Format (CEF / RFC 5424)",
        "cef_raw_log": cef_string,
        "siem_compatibility": ["Splunk Enterprise Security", "Elastic SIEM", "Microsoft Sentinel", "IBM QRadar"],
        "severity": 10 if enforcement_level == "ISOLATE" else 8 if enforcement_level == "QUARANTINE" else 5
    }


@router.get("/api/soc/stix-bundle")
def get_stix_threat_intel(attack_type: str = Query("INTERCEPT_RESEND"),
                          session_id: str = Query("SESS-ADV-7741")) -> Dict[str, Any]:
    """
    Generates an OASIS STIX 2.1 Cyber Threat Intelligence JSON bundle
    mapped to MITRE ATT&CK for Quantum Networks.
    """
    meta = ATTACK_PROFILES_METADATA.get(attack_type, {})
    mitre_id = meta.get("mitre_id", "T1557.002")
    mitre_name = meta.get("name", "Quantum Man-in-the-Middle")
    threat_desc = meta.get("description", "Adversary intercepts quantum channel.")

    return SHARED_SOC_ENGINE.generate_stix_21_bundle(
        session_id=session_id,
        attack_type=attack_type,
        mitre_id=mitre_id,
        mitre_name=mitre_name,
        threat_description=threat_desc,
        qber=0.25,
        enforcement="ISOLATE"
    )


@router.post("/api/soc/active-defense")
def generate_active_defense_playbook(req: FirewallPlaybookRequest) -> Dict[str, Any]:
    """
    Generates automated containment commands for Zero-Trust network infrastructure:
    Linux iptables/nftables, Cisco core router ACLs, and SDN OpenFlow flow-mod commands.
    Follows NIST SP 800-61 Rev. 2 Incident Response.
    """
    try:
        return SHARED_SOC_ENGINE.generate_active_firewall_playbook(
            session_id=req.session_id,
            threat_type=req.threat_type,
            enforcement_level=req.enforcement_level,
            adversary_ip=req.adversary_ip,
            affected_optical_port=req.affected_optical_port
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
