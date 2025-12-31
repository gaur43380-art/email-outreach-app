#email_log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from backend.db.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)

    # ----------------------------------
    # Relations
    # ----------------------------------
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    to_email = Column(String, index=True)

    # ----------------------------------
    # Status tracking
    # ----------------------------------
    status = Column(String, index=True)
    # SENT | FOLLOWUP_1 | FOLLOWUP_2 | REPLIED | BOUNCED | FAILED

    # ✅ CHANGED: Renamed from error_message to error (to match gmail_service.py)
    error = Column(String, nullable=True)

    # ----------------------------------
    # Timestamp
    # ----------------------------------
    sent_at = Column(DateTime, default=datetime.utcnow)