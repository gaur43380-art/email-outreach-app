#user.py
from sqlalchemy import Column, Integer, String, Boolean, Text
from backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ----------------------------------
    # Website login credentials
    # ----------------------------------
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # ----------------------------------
    # ✅ NEW: User's actual name (for emails)
    # ----------------------------------
    full_name = Column(String, nullable=True)

    # ----------------------------------
    # Roles & controls
    # ----------------------------------
    is_admin = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)

    # ----------------------------------
    # Gmail OAuth (user-specific)
    # ----------------------------------
    gmail_token_path = Column(String, nullable=True)

    # ----------------------------------
    # Google Sheet linked to this user
    # ----------------------------------
    sheet_id = Column(String, nullable=True)
    
    # ----------------------------------
    # Email personalization
    # ----------------------------------
    email_template = Column(Text, nullable=True)       # Initial email template
    followup_template = Column(Text, nullable=True)    # ✅ NEW: Follow-up email template
    email_subject = Column(String, nullable=True)      # ✅ NEW: Email subject line
    resume_link = Column(String, nullable=True)