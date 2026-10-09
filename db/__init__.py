"""
db/__init__.py
QuantumGuard QDS Database & Infrastructure Package.
Provides relational ORM models, migration hooks, persistent ledger repositories,
and sub-microsecond atomic Redis state caching.
"""

from db.base import (
    Base,
    engine,
    SessionLocal,
    get_db,
    get_db_context,
    init_db,
    DATABASE_URL,
)

from db.models import (
    User,
    UserRole,
    SessionRecord,
    LedgerBlock,
    TelemetryLog,
)

from db.repositories import (
    create_session,
    burn_session_db,
    get_session,
    append_block,
    get_blocks,
    get_last_block,
    log_telemetry,
    verify_ledger_integrity,
    calculate_block_hash,
    PersistentCryptographicAuditLedger,
)

from db.redis_cache import (
    RedisStateCache,
    RedisCacheError,
    ReplayAttackDetectedError,
    CacheFailClosedError,
)

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db",
    "DATABASE_URL",
    "User",
    "UserRole",
    "SessionRecord",
    "LedgerBlock",
    "TelemetryLog",
    "create_session",
    "burn_session_db",
    "get_session",
    "append_block",
    "get_blocks",
    "get_last_block",
    "log_telemetry",
    "verify_ledger_integrity",
    "calculate_block_hash",
    "PersistentCryptographicAuditLedger",
    "RedisStateCache",
    "RedisCacheError",
    "ReplayAttackDetectedError",
    "CacheFailClosedError",
]
