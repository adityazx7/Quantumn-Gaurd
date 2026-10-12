"""
db/base.py
Database Engine, Session, and Base declarative model definition.
Supports PostgreSQL (production) and SQLite (testing/local fallback)
with robust environment configuration and URL escaping.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


def _load_env_file():
    """Lightweight .env loader if python-dotenv is not installed."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    # Let file define or override empty
                    if k not in os.environ or not os.environ[k]:
                        os.environ[k] = v


_load_env_file()


def get_database_url() -> str:
    """Builds or returns a safe DATABASE_URL with encoded credentials."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Fallback construct from individual variables
    user = os.getenv("POSTGRES_USER", "postgres")
    password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "quantumguard")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = get_database_url()

# Connect args (e.g. sqlite check_same_thread)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency helper for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for scripts, services, and tasks."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initializes schema tables directly using Base.metadata."""
    # Ensure models are imported so Base.metadata knows about them
    import db.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
