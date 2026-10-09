"""
scripts/backup_db.py
Automated Database Backup Tool for QuantumGuard QDS.
Generates timestamped, gzip-compressed SQL dumps of the PostgreSQL database.
"""

import os
import sys
import time
import gzip
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import DATABASE_URL

BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"


def backup_database() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"quantumguard_backup_{timestamp}.sql.gz"

    print(f"[*] Starting backup of QuantumGuard database at {time.ctime()}...")

    parsed = urlparse(DATABASE_URL)
    user = parsed.username or "postgres"
    password = unquote(parsed.password) if parsed.password else "postgres"

    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/") or "quantumguard"

    # Find pg_dump
    pg_dump_cmd = "pg_dump"
    # Check default Postgres installation on Windows if pg_dump not on PATH
    if shutil.which("pg_dump") is None:
        win_candidates = [
            r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
        ]
        for c in win_candidates:
            if os.path.exists(c):
                pg_dump_cmd = c
                break

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    cmd = [
        pg_dump_cmd,
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", dbname,
        "--clean",
        "--if-exists"
    ]

    print(f"[*] Executing pg_dump against {host}:{port}/{dbname}...")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"pg_dump failed with code {proc.returncode}: {stderr.decode(errors='replace')}")

        with gzip.open(backup_file, "wb") as gz:
            gz.write(stdout)

        size_kb = os.path.getsize(backup_file) / 1024
        print(f"[SUCCESS] Database successfully backed up to: {backup_file} ({size_kb:.2f} KB)")
        return backup_file
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")
        raise


if __name__ == "__main__":
    backup_database()
