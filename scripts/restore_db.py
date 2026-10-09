"""
scripts/restore_db.py
Database Restore Tool for QuantumGuard QDS.
Restores a PostgreSQL database from a gzip-compressed or raw SQL dump file.
"""

import os
import sys
import gzip
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import DATABASE_URL


def restore_database(backup_path: str):
    file_path = Path(backup_path).resolve()
    if not file_path.exists():
        print(f"[ERROR] Backup file does not exist: {file_path}")
        sys.exit(1)

    print(f"[*] Restoring QuantumGuard database from: {file_path}...")

    parsed = urlparse(DATABASE_URL)
    user = parsed.username or "postgres"
    password = unquote(parsed.password) if parsed.password else "postgres"

    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/") or "quantumguard"

    # Find psql
    psql_cmd = "psql"
    if shutil.which("psql") is None:
        win_candidates = [
            r"C:\Program Files\PostgreSQL\18\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        ]
        for c in win_candidates:
            if os.path.exists(c):
                psql_cmd = c
                break

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # Decompress SQL if gzipped
    if file_path.suffix == ".gz":
        print("[*] Decompressing gzip archive...")
        with gzip.open(file_path, "rb") as gz:
            sql_data = gz.read()
    else:
        with open(file_path, "rb") as f:
            sql_data = f.read()

    cmd = [
        psql_cmd,
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", dbname
    ]

    print(f"[*] Applying SQL stream to {host}:{port}/{dbname}...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate(input=sql_data)

    if proc.returncode != 0:
        print(f"[ERROR] Restore failed with code {proc.returncode}: {stderr.decode(errors='replace')}")
        sys.exit(proc.returncode)

    print("[SUCCESS] Database restore successfully completed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # If no argument passed, search for most recent backup in backups/
        backup_dir = Path(__file__).resolve().parent.parent / "backups"
        backups = sorted(backup_dir.glob("quantumguard_backup_*.sql.gz"), reverse=True)
        if not backups:
            print("Usage: python scripts/restore_db.py <path_to_backup.sql.gz>")
            sys.exit(1)
        target = str(backups[0])
        print(f"[*] No backup specified; using latest discovered backup: {target}")
    else:
        target = sys.argv[1]

    restore_database(target)
