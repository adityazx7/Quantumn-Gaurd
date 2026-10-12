"""
api/services/auth_service.py
Layer 4 Authentication & Multi-Party Signature Service.
Implements JWT tokens and bcrypt hashing for distinct cryptographic entities:
- Alice (Signer)
- Bob (Verifier 1)
- Charlie (Verifier 2)
- Auditor (Auditor)
"""

import os
import time
import secrets
import bcrypt
import jwt
from typing import Dict, Any, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET_KEY = os.getenv("QUANTUMGUARD_JWT_SECRET", "quantum-guard-its-jwt-secret-key-2026-sih26141")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

security_bearer = HTTPBearer(auto_error=False)

# Seed predefined cryptographic entity credentials
DEFAULT_USERS: Dict[str, Dict[str, Any]] = {
    "alice": {
        "username": "alice",
        "password_hash": bcrypt.hashpw(b"alice_signer_2026", bcrypt.gensalt()).decode("utf-8"),
        "entity_name": "Alice (Signer / State Preparer)",
        "role": "signer",
        "public_key_fingerprint": "SHA256:7e9a4f21b44c8c29e1fa3d6290812b1c",
        "description": "Cryptographic Signer preparing Pauli eigenstate signatures and Bell projections."
    },
    "bob": {
        "username": "bob",
        "password_hash": bcrypt.hashpw(b"bob_verifier_2026", bcrypt.gensalt()).decode("utf-8"),
        "entity_name": "Bob (Primary Verifier)",
        "role": "verifier_1",
        "public_key_fingerprint": "SHA256:91b2c45e89a311c6d7023ef0aa482901",
        "description": "Primary verifier reconstructing teleported states via Pauli unitary corrections."
    },
    "charlie": {
        "username": "charlie",
        "password_hash": bcrypt.hashpw(b"charlie_verifier_2026", bcrypt.gensalt()).decode("utf-8"),
        "entity_name": "Charlie (Consensus Verifier)",
        "role": "verifier_2",
        "public_key_fingerprint": "SHA256:334f590ac1287e59b20d312109ab77c4",
        "description": "Consensus verifier participating in the ECS cross-verifier anti-repudiation test."
    },
    "auditor": {
        "username": "auditor",
        "password_hash": bcrypt.hashpw(b"auditor_pass_2026", bcrypt.gensalt()).decode("utf-8"),
        "entity_name": "Security Auditor",
        "role": "auditor",
        "public_key_fingerprint": "SHA256:889ac4112e79fa3009bc245100fae120",
        "description": "Compliance and ledger integrity officer verifying chained SHA-256 blocks."
    }
}


class AuthService:
    """Authentication and multi-party JWT identity management."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plaintext password against stored bcrypt hash."""
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @classmethod
    def authenticate_entity(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates entity credentials."""
        user = DEFAULT_USERS.get(username.lower())
        if not user:
            return None
        if not cls.verify_password(password, user["password_hash"]):
            return None
        return {
            "username": user["username"],
            "entity_name": user["entity_name"],
            "role": user["role"],
            "public_key_fingerprint": user["public_key_fingerprint"],
            "description": user["description"]
        }

    @classmethod
    def create_access_token(cls, user_data: Dict[str, Any], expires_in_minutes: int = JWT_EXPIRATION_MINUTES) -> str:
        """Issues signed JWT access token."""
        now = int(time.time())
        payload = {
            "sub": user_data["username"],
            "role": user_data["role"],
            "entity_name": user_data["entity_name"],
            "iat": now,
            "exp": now + (expires_in_minutes * 60)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        """Decodes and validates JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please log in again."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid cryptographic authentication token."
            )

    @classmethod
    def get_all_entities(cls) -> List[Dict[str, Any]]:
        """Returns public metadata of all pre-registered entities."""
        entities = []
        for user in DEFAULT_USERS.values():
            entities.append({
                "username": user["username"],
                "entity_name": user["entity_name"],
                "role": user["role"],
                "public_key_fingerprint": user["public_key_fingerprint"],
                "description": user["description"]
            })
        return entities


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> Dict[str, Any]:
    """FastAPI dependency to extract and validate entity from Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization Bearer token is missing."
        )
    return AuthService.decode_token(credentials.credentials)


def require_role(allowed_roles: List[str]):
    """Role-based authorization dependency factory."""
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{user.get('role')}'. Required roles: {allowed_roles}"
            )
        return user
    return role_checker
