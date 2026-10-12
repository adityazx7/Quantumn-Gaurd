"""
api/routers/auth.py
FastAPI router for cryptographic entity authentication and multi-party signature verification.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status

from api.schemas.auth import (
    LoginRequest,
    TokenResponse,
    MultiPartyVerifyRequest,
    MultiPartyVerifyResponse
)
from api.services.auth_service import AuthService, get_current_user, require_role
from api.services.qkd_service import SHARED_QKD_SERVICE

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest) -> Dict[str, Any]:
    """Authenticates a cryptographic entity (Alice, Bob, Charlie, Auditor) and issues a JWT."""
    entity = AuthService.authenticate_entity(req.username, req.password)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid cryptographic entity credentials."
        )
    token = AuthService.create_access_token(entity)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": 60,
        "user": entity
    }


@router.get("/me")
def get_current_entity(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Returns the authenticated entity's identity and cryptographic role."""
    return current_user


@router.get("/entities")
def get_entities() -> List[Dict[str, Any]]:
    """Returns directory of public keys and roles for all pre-registered cryptographic entities."""
    return AuthService.get_all_entities()


@router.post("/verify-signature", response_model=MultiPartyVerifyResponse)
def verify_multi_party_signature(
    req: MultiPartyVerifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Executes multi-party signature verification:
    Alice transmits quantum signature to Bob (Verifier 1) and Charlie (Verifier 2).
    Requires authenticated user.
    """
    signer_name = current_user.get("entity_name", "Alice (Signer)")
    result = SHARED_QKD_SERVICE.execute_multi_party_signature(
        signer=signer_name,
        verifiers=["Bob (Verifier 1)", "Charlie (Verifier 2)"],
        message=req.message,
        L=req.L,
        channel_noise=req.channel_noise,
        simulate_attack=req.simulate_attack or "NONE"
    )
    return result
