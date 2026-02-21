"""
RequirementIQ — MySQL Database Connection
SQLAlchemy engine + session factory + helper utilities.
"""
import uuid
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from config import settings


# ── Engine ────────────────────────────────────────────────────
engine = create_engine(
    settings.db_url,
    pool_size=settings.db_pool_size,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,          # Detect stale connections
    echo=not settings.is_production,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ── Base Model ────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Session context manager ───────────────────────────────────
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Usage:
        with get_db() as db:
            result = db.execute(text("SELECT 1"))
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Utilities ─────────────────────────────────────────────────
def new_uuid() -> str:
    return str(uuid.uuid4())


def test_connection() -> bool:
    """Returns True if the database is reachable."""
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        return False


def init_db() -> None:
    """
    Run schema.sql if tables don't exist yet.
    Call this once at application startup.
    """
    import os
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        print("[DB] schema.sql not found, skipping auto-init.")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Split on semicolons and execute each statement
    with engine.connect() as conn:
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                try:
                    conn.execute(text(statement))
                except Exception as e:
                    # Ignore "already exists" errors during re-init
                    if "already exists" not in str(e).lower():
                        print(f"[DB] Init warning: {e}")
        conn.commit()
    print("[DB] Schema initialized successfully.")
