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

# Create credentials directory if it doesn't exist (for local dev)
CREDENTIALS_DIR.mkdir(exist_ok=True)

# ======================================================
# APP SETTINGS
# ======================================================

APP_NAME = "Email Outreach App"
ENV = os.getenv("ENV", "development")

# SECRET KEY - Must be set in production
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if ENV == "production":
        raise ValueError("SECRET_KEY environment variable must be set in production")
    else:
        SECRET_KEY = "dev-secret-key-change-in-production"

# ======================================================
# DATABASE
# ======================================================

# Get DATABASE_URL from environment (Render provides this for PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle Render's postgres:// vs postgresql:// issue
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fallback to SQLite for local development
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR}/email_outreach.db"

# ======================================================
# GOOGLE OAUTH (GMAIL)
# ======================================================

# ✅ UPDATED: Check multiple locations for credentials
def get_credential_path(filename):
    """
    Find credential file in multiple possible locations:
    1. /etc/secrets/ (Render's secret files location)
    2. Root directory (alternative Render location)
    3. credentials/ directory (local development)
    """
    possible_paths = [
        Path(f"/etc/secrets/{filename}"),           # Render secret files
        BASE_DIR / filename,                         # Root level
        CREDENTIALS_DIR / filename,                  # Local dev
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"Found {filename} at: {path}")
            return path
    
    # If not found, return default path (will fail later with clear error)
    print(f"Warning: {filename} not found in any location")
    return CREDENTIALS_DIR / filename

# OAuth client secret
GMAIL_CLIENT_SECRET_FILE = get_credential_path("client_secret.json")

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

# Service account JSON
SHEETS_SERVICE_ACCOUNT_FILE = get_credential_path("sheets_service.json")

# Sheet settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "Sheet1")

# ======================================================
# EMAIL SENDING RULES (SAFE LIMITS)
# ======================================================

MAX_EMAILS_PER_DAY = int(os.getenv("MAX_EMAILS_PER_DAY", "50"))
MIN_DELAY_SECONDS = int(os.getenv("MIN_DELAY_SECONDS", "120"))
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", "300"))

MAX_FOLLOWUPS = int(os.getenv("MAX_FOLLOWUPS", "5"))
FOLLOWUP_2_DELAY_DAYS = int(os.getenv("FOLLOWUP_2_DELAY_DAYS", "60"))

# ======================================================
# LOGGING
# ======================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ======================================================
# WEBSITE AUTH (FIXED ACCESS GATE)
# ======================================================

WEBSITE_ACCESS_ID = os.getenv("WEBSITE_ACCESS_ID", "admin")
WEBSITE_ACCESS_PASSWORD = os.getenv("WEBSITE_ACCESS_PASSWORD", "admin123")

# ======================================================
# RENDER / DEPLOYMENT
# ======================================================

PORT = int(os.getenv("PORT", "8000"))

# ======================================================
# REDIRECT URI (for Gmail OAuth)
# ======================================================

if ENV == "development":
    GMAIL_REDIRECT_URI = "http://localhost:8000/auth/gmail/callback"
else:
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
    print(f"Gmail Client Secret: {GMAIL_CLIENT_SECRET_FILE}")
    print(f"Sheets Service Account: {SHEETS_SERVICE_ACCOUNT_FILE}")
    print(f"Gmail Redirect URI: {GMAIL_REDIRECT_URI}")
    print(f"Max Emails/Day: {MAX_EMAILS_PER_DAY}")
    print(f"Gate ID: {WEBSITE_ACCESS_ID}")
    print("=" * 60)