# backend/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

from backend.config import DATABASE_URL

# ======================================================
# DATABASE ENGINE
# ======================================================

# ✅ Conditionally add connect_args only for SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Only for SQLite

engine: Engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,  # ✅ Empty dict for PostgreSQL, SQLite args for SQLite
    pool_size=5,                # Increased pool size
    max_overflow=10,             # Increased overflow
    pool_pre_ping=True,          # Verify connections before using
    pool_recycle=3600            # Recycle connections after 1 hour
)

# ======================================================
# SESSION
# ======================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ======================================================
# BASE MODEL
# ======================================================

Base = declarative_base()

# ======================================================
# DEPENDENCY (FastAPI)
# ======================================================

def get_db():
    """
    FastAPI dependency to get DB session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()