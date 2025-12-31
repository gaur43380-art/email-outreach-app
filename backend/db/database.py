from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

from backend.config import DATABASE_URL

# ======================================================
# DATABASE ENGINE
# ======================================================

engine: Engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    pool_size=20,           # ✅ Increased from default 5
    max_overflow=40,        # ✅ Increased from default 10
    pool_pre_ping=True,     # ✅ Verify connections before using
    pool_recycle=3600       # ✅ Recycle connections after 1 hour
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