# backend/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ======================================================
# BASE PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_DIR = BASE_DIR / "credentials"
ASSETS_DIR = BASE_DIR / "assets"

# ======================================================
# APP SETTINGS
# ======================================================

APP_NAME = "Email Outreach App"
ENV = os.getenv("ENV", "development")

# ✅ SECRET KEY - Must be set in production
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if ENV == "production":
        raise ValueError("SECRET_KEY environment variable must be set in production")
    else:
        # Use a default key for development only
        SECRET_KEY = "dev-secret-key-change-in-production"

# ======================================================
# DATABASE
# ======================================================

# ✅ Get DATABASE_URL from environment (Render provides this for PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Handle Render's postgres:// vs postgresql:// issue
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ✅ Fallback to SQLite for local development
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR}/email_outreach.db"

# ======================================================
# GOOGLE OAUTH (GMAIL)
# ======================================================

# OAuth client secret downloaded from Google Cloud Console
GMAIL_CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"

# Where user Gmail tokens will be stored
GMAIL_TOKEN_DIR = BASE_DIR / "tokens"
GMAIL_TOKEN_DIR.mkdir(exist_ok=True)

# Gmail API scopes
GMAIL_SCOPES_STRING = os.getenv(
    "GMAIL_SCOPES", 
    "https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.readonly"
)
GMAIL_SCOPES = GMAIL_SCOPES_STRING.split(",")

# ======================================================
# GOOGLE SHEETS (SERVICE ACCOUNT)
# ======================================================

# Service account JSON downloaded from Google Cloud Console
SHEETS_SERVICE_ACCOUNT_FILE = CREDENTIALS_DIR / "sheets_service.json"

# Sheet settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "Sheet1")

# ======================================================
# EMAIL SENDING RULES (SAFE LIMITS)
# ======================================================

# Gmail safe sending limits (FREE Gmail)
MAX_EMAILS_PER_DAY = int(os.getenv("MAX_EMAILS_PER_DAY", "50"))
MIN_DELAY_SECONDS = int(os.getenv("MIN_DELAY_SECONDS", "120"))
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", "300"))

# Follow-up rules
MAX_FOLLOWUPS = int(os.getenv("MAX_FOLLOWUPS", "5"))
FOLLOWUP_2_DELAY_DAYS = int(os.getenv("FOLLOWUP_2_DELAY_DAYS", "60"))

# ======================================================
# LOGGING
# ======================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ======================================================
# WEBSITE AUTH (FIXED ACCESS GATE)
# ======================================================

# Simple gate login (must be set via environment variables in production)
WEBSITE_ACCESS_ID = os.getenv("WEBSITE_ACCESS_ID", "admin")
WEBSITE_ACCESS_PASSWORD = os.getenv("WEBSITE_ACCESS_PASSWORD", "admin123")

# ======================================================
# RENDER / DEPLOYMENT
# ======================================================

PORT = int(os.getenv("PORT", "8000"))

# ======================================================
# REDIRECT URI (for Gmail OAuth)
# ======================================================

# ✅ Dynamic redirect URI based on environment
if ENV == "development":
    # For local development
    GMAIL_REDIRECT_URI = "http://localhost:8000/auth/gmail/callback"
else:
    # For production (Render)
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
    if not RENDER_EXTERNAL_URL:
        raise ValueError("RENDER_EXTERNAL_URL environment variable must be set in production")
    GMAIL_REDIRECT_URI = f"{RENDER_EXTERNAL_URL}/auth/gmail/callback"

# ======================================================
# DEBUG INFO (only print in development)
# ======================================================

if ENV == "development":
    print("=" * 60)
    print("🔧 CONFIGURATION LOADED")
    print("=" * 60)
    print(f"Environment: {ENV}")
    print(f"Database: {DATABASE_URL}")
    print(f"Gmail Redirect URI: {GMAIL_REDIRECT_URI}")
    print(f"Max Emails/Day: {MAX_EMAILS_PER_DAY}")
    print(f"Gate ID: {WEBSITE_ACCESS_ID}")
    print("=" * 60)