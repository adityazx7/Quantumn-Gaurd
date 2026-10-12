"""
scripts/enforce_append_only_trigger.py
Enforces hardware/DB-level append-only immutability on table `ledger_blocks`.
Installs a PostgreSQL trigger that aborts any UPDATE or DELETE statement.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import engine
from sqlalchemy import text


def apply_immutability_trigger():
    sql = """
    CREATE OR REPLACE FUNCTION prevent_ledger_tampering()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'TAMPER ATTEMPT BLOCKED: ledger_blocks is strictly append-only. Modification or deletion is forbidden.';
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_ledger_blocks_immutable ON ledger_blocks;

    CREATE TRIGGER trg_ledger_blocks_immutable
    BEFORE UPDATE OR DELETE ON ledger_blocks
    FOR EACH ROW
    EXECUTE FUNCTION prevent_ledger_tampering();
    """

    if not str(engine.url).startswith("postgresql"):
        print("[*] Non-PostgreSQL database detected; skipping PostgreSQL trigger.")
        return

    with engine.begin() as conn:
        conn.execute(text(sql))
    print("[SUCCESS] PostgreSQL immutable append-only trigger installed on table 'ledger_blocks'!")


if __name__ == "__main__":
    apply_immutability_trigger()
