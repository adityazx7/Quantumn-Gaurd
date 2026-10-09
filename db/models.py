"""
db/models.py
SQLAlchemy 2.0 ORM models for QuantumGuard QDS.
Defines 4 tables:
1. users: Authentication credentials and roles (SIGNER, VERIFIER, AUDITOR)
2. sessions: Cryptographic quantum sessions with monotonic SIDs
3. ledger_blocks: Immutable SHA-256 chained PBFT ledger blocks
4. telemetry_logs: Detailed quantum physics observables and QBER metrics
"""

import enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, Enum, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from db.base import Base


class UserRole(str, enum.Enum):
    SIGNER = "SIGNER"
    VERIFIER = "VERIFIER"
    AUDITOR = "AUDITOR"


class User(Base):
    """Users table for cryptographic entities and administrative access."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.VERIFIER
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    sessions = relationship("SessionRecord", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value if isinstance(self.role, UserRole) else str(self.role),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SessionRecord(Base):
    """Sessions table recording monotonic SIDs and payload telemetry."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sid = Column(String(128), unique=True, index=True, nullable=False)
    message_hash = Column(String(64), nullable=False)
    payload = Column(Text, nullable=True)
    L = Column(Integer, default=128, nullable=False)
    attack_type = Column(String(64), default="NONE", nullable=False)
    status = Column(String(64), default="ACTIVE", nullable=False)  # ACTIVE, BURNED, REPLAY_REJECTED
    decision = Column(String(32), nullable=True)                  # ACCEPTED, REJECTED
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    ledger_blocks = relationship("LedgerBlock", back_populates="session")
    telemetry_logs = relationship("TelemetryLog", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sid": self.sid,
            "message_hash": self.message_hash,
            "payload": self.payload,
            "L": self.L,
            "attack_type": self.attack_type,
            "status": self.status,
            "decision": self.decision,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
        }


class LedgerBlock(Base):
    """Chained SHA-256 PBFT cryptographic audit ledger block."""
    __tablename__ = "ledger_blocks"

    block_index = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(128), ForeignKey("sessions.sid", ondelete="SET NULL"), nullable=True, index=True)
    block_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    qber = Column(Float, nullable=False)
    s_value = Column(Float, nullable=False)  # CHSH S correlation parameter
    enforcement_level = Column(String(32), nullable=False)  # MONITOR, RESTRICT, QUARANTINE, ISOLATE
    timestamp = Column(Float, nullable=False)
    formatted_time = Column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_ledger_blocks_hash", "block_hash"),
    )

    # Relationships
    session = relationship("SessionRecord", back_populates="ledger_blocks")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.block_index,
            "timestamp": self.timestamp,
            "formatted_time": self.formatted_time,
            "session_id": self.session_id,
            "block_hash": self.block_hash,
            "hash": self.block_hash,  # alias for backwards compatibility with core/state_registry
            "previous_hash": self.previous_hash,
            "qber": round(float(self.qber), 4),
            "chsh_s": round(float(self.s_value), 4),
            "enforcement_level": self.enforcement_level,
        }


class TelemetryLog(Base):
    """Telemetry logs recording raw quantum metrics and physics observables."""
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(128), ForeignKey("sessions.sid", ondelete="SET NULL"), nullable=True, index=True)
    qber = Column(Float, nullable=False)
    e_x = Column(Float, nullable=True)
    e_y = Column(Float, nullable=True)
    e_z = Column(Float, nullable=True)
    basis_asymmetry = Column(Float, nullable=True)
    grover_score = Column(Float, nullable=True)
    execution_ms = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    session = relationship("SessionRecord", back_populates="telemetry_logs")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "qber": round(float(self.qber), 4),
            "e_x": round(float(self.e_x), 4) if self.e_x is not None else None,
            "e_y": round(float(self.e_y), 4) if self.e_y is not None else None,
            "e_z": round(float(self.e_z), 4) if self.e_z is not None else None,
            "basis_asymmetry": round(float(self.basis_asymmetry), 4) if self.basis_asymmetry is not None else None,
            "grover_score": round(float(self.grover_score), 4) if self.grover_score is not None else None,
            "execution_ms": round(float(self.execution_ms), 4) if self.execution_ms is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
