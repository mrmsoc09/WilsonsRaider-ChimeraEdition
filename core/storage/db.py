from __future__ import annotations
import os
from pathlib import Path
from sqlalchemy import create_engine

DEFAULT_SQLITE_PATH = os.getenv("WR_SQLITE_PATH", "data/wr.db")
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_SQLITE_PATH}"

def get_engine():
    # Ensure SQLite directory exists
    if DATABASE_URL.startswith("sqlite:"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
    return engine

