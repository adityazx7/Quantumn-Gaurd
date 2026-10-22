"""
api/routers/attacks.py
FastAPI router for Adversarial Attack Simulation, Real-World Test Cases,
MITRE ATT&CK Mapping, and SciPy Benchmark Sweeps.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from api.services.qkd_service import SHARED_QKD_SERVICE
from api.schemas.simulation import AdversarySimulateRequest, TestCaseExecuteRequest
from core.real_test_cases import RealTestCaseService
from core.adversarial_engine import ConfigurableAdversaryEngine

router = APIRouter(tags=["attacks"])


@router.get("/api/benchmark")
async def get_benchmark() -> Dict[str, Any]:
    """Runs SciPy Chernoff-Hoeffding exact benchmark sweep across L=16 to 1024."""
    try:
        return await SHARED_QKD_SERVICE.run_benchmark_async()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/attack-matrix")
async def get_attack_matrix(L: int = 128) -> List[Dict[str, Any]]:
    """Generates comparison matrix across all attack vectors + baseline."""
    try:
        return await SHARED_QKD_SERVICE.run_attack_matrix_async(L=L)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/test-cases")
def list_test_cases() -> List[Dict[str, Any]]:
    """Returns the library of real-world enterprise, banking, SCADA, aerospace, and Web3 test cases."""
    try:
        return RealTestCaseService.list_test_cases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/test-cases/{case_id}")
def get_test_case_details(case_id: str) -> Dict[str, Any]:
    """Fetches payload structure and tamper options for a specific test case."""
    case = RealTestCaseService.get_test_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Test case '{case_id}' not found.")
    return case


@router.post("/api/test-cases/execute")
async def execute_test_case(req: TestCaseExecuteRequest) -> Dict[str, Any]:
    """
    Executes quantum digital signature verification against a real structured payload.
    Supports selective field-level tampering (e.g. modifying SWIFT beneficiary IBAN).
    """
    try:
        result = await SHARED_QKD_SERVICE.run_simulation_async(
            L=req.L,
            attack_type="FORGERY" if req.tamper_payload else "NONE",
            channel_noise=req.channel_noise,
            test_case_id=req.test_case_id,
            tamper_payload=req.tamper_payload
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/adversary/profiles")
def list_adversary_profiles() -> List[Dict[str, Any]]:
    """Returns MITRE ATT&CK mapped quantum attack vectors with descriptions and default parameters."""
    try:
        return ConfigurableAdversaryEngine.list_attack_profiles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/adversary/simulate")
async def simulate_adversary_attack(req: AdversarySimulateRequest) -> Dict[str, Any]:
    """
    Executes red-team adversarial attack simulation against real structured test cases.
    Allows configuring eavesdropping fraction eta, basis, and target field tampering.
    """
    try:
        result = await SHARED_QKD_SERVICE.run_adversary_simulation_async(
            attack_type=req.attack_type,
            test_case_id=req.test_case_id,
            eavesdrop_fraction=req.eavesdrop_fraction,
            adversary_basis=req.adversary_basis,
            channel_noise=req.channel_noise,
            L=req.L,
            custom_message=req.custom_message,
            sid=req.sid
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
