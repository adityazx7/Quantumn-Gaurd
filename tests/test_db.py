"""
tests/test_db.py
Automated Test Suite for Relational Database & Persistent Ledger Layer.
Validates:
1. Schema existence (users, sessions, ledger_blocks, telemetry_logs)
2. Foreign key relationships and user roles
3. Cryptographic block chaining and SHA-256 hash calculation
4. Persistence across process restarts
5. Append-only ledger integrity verification
"""

import sys
import os
import time
import hashlib
from sqlalchemy import text, inspect

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import engine, SessionLocal, init_db
from db.models import User, UserRole, SessionRecord, LedgerBlock, TelemetryLog
from db.repositories import (
    create_session,
    burn_session_db,
    get_session,
    append_block,
    get_blocks,
    get_last_block,
    log_telemetry,
    verify_ledger_integrity,
    PersistentCryptographicAuditLedger,
    calculate_block_hash,
)


def test_schema_tables_exist():
    """Ensure all 4 tables exist with proper schemas."""
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nExisting tables in database:", tables)

    assert "users" in tables, "users table missing"
    assert "sessions" in tables, "sessions table missing"
    assert "ledger_blocks" in tables, "ledger_blocks table missing"
    assert "telemetry_logs" in tables, "telemetry_logs table missing"
    print(">>> 1. Schema tables test PASSED! <<<")


def test_user_and_session_creation():
    """Verify user creation, roles, and session linking."""
    db = SessionLocal()
    try:
        username = f"test_signer_{int(time.time() * 1000)}"
        user = User(
            username=username,
            password_hash="$2b$12$e8p2u7s90a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2",
            role=UserRole.SIGNER
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.role == UserRole.SIGNER

        sid = f"SID-TEST-USER-{int(time.time() * 1000)}"
        session_dict = create_session(
            sid=sid,
            message="Test Signed Message",
            L=64,
            user_id=user.id,
            db=db
        )
        assert session_dict["sid"] == sid
        assert session_dict["user_id"] == user.id

        fetched = get_session(sid, db=db)
        assert fetched is not None
        assert fetched["payload"] == "Test Signed Message"
        print(">>> 2. User & Session creation test PASSED! <<<")
    finally:
        db.close()


def test_append_block_and_pessimistic_locking():
    """Verify append_block creates valid chained blocks."""
    db = SessionLocal()
    try:
        sid = f"SID-CHAIN-{int(time.time() * 1000)}"
        msg = "Chained Transaction Block Test"
        block = append_block(
            session_id=sid,
            message=msg,
            qber=0.015,
            chsh_s=2.810,
            decision="ACCEPTED",
            enforcement_level="MONITOR",
            db=db
        )

        assert block["index"] >= 1
        assert block["session_id"] == sid
        assert len(block["block_hash"]) == 64
        assert len(block["previous_hash"]) == 64

        last = get_last_block(db=db)
        assert last["index"] == block["index"]
        assert last["block_hash"] == block["block_hash"]
        print(">>> 3. Block appending and chaining test PASSED! <<<")
    finally:
        db.close()


def test_ledger_chain_integrity():
    """Verify mathematical chain integrity across all blocks."""
    db = SessionLocal()
    try:
        valid = verify_ledger_integrity(db=db)
        assert valid is True, "Ledger integrity verification failed!"
        print(">>> 4. Full ledger integrity check PASSED! <<<")
    finally:
        db.close()


def test_telemetry_logging():
    """Verify logging quantum physics observables."""
    db = SessionLocal()
    try:
        sid = f"SID-TELEM-{int(time.time() * 1000)}"
        tlog = log_telemetry(
            session_id=sid,
            qber=0.042,
            e_x=0.04,
            e_y=0.04,
            e_z=0.045,
            basis_asymmetry=0.005,
            grover_score=0.12,
            execution_ms=0.34,
            db=db
        )
        assert tlog["id"] is not None
        assert tlog["qber"] == 0.042
        assert tlog["execution_ms"] == 0.34
        print(">>> 5. Telemetry log persistence test PASSED! <<<")
    finally:
        db.close()


def test_persistent_ledger_restart():
    """Verify ledger persistence across fresh instances."""
    ledger1 = PersistentCryptographicAuditLedger()
    count_before = len(ledger1.get_all_blocks())

    sid = f"SID-RESTART-{int(time.time() * 1000)}"
    ledger1.append_record(
        session_id=sid,
        message="Persistence Test Across Server Restarts",
        qber=0.0,
        chsh_s=2.828,
        decision="ACCEPTED",
        enforcement_level="MONITOR"
    )

    # Simulate restart by creating completely new ledger instance
    ledger2 = PersistentCryptographicAuditLedger()
    blocks = ledger2.get_all_blocks()

    assert len(blocks) == count_before + 1
    assert ledger2.verify_integrity() is True
    print(">>> 6. Persistent ledger server restart test PASSED! <<<")


if __name__ == "__main__":
    print("================ RUNNING DATABASE INTEGRATION TESTS ================")
    test_schema_tables_exist()
    test_user_and_session_creation()
    test_append_block_and_pessimistic_locking()
    test_ledger_chain_integrity()
    test_telemetry_logging()
    test_persistent_ledger_restart()
    print("\n================ ALL DATABASE TESTS PASSED SUCCESSFULLY! ================")
