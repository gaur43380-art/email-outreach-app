# backend/auth/gmail_oauth.py

import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.user import User
from backend.config import GMAIL_SCOPES, GMAIL_CLIENT_SECRET_FILE, GMAIL_REDIRECT_URI

router = APIRouter()

# -----------------------------
# Google OAuth Config
# -----------------------------

TOKEN_DIR = "tokens"
os.makedirs(TOKEN_DIR, exist_ok=True)


def get_token_path(user_id: int) -> str:
    """Each user has their own Gmail token JSON file"""
    return os.path.join(TOKEN_DIR, f"gmail_token_user_{user_id}.json")


# -----------------------------
# Routes
# -----------------------------
@router.get("/auth/gmail/connect")
def connect_gmail(request: Request):
    """Redirect user to Google consent screen"""
    user_id = request.session.get("user_id")
    if not user_id:
        return {"error": "User not logged in"}

    flow = Flow.from_client_secrets_file(
        str(GMAIL_CLIENT_SECRET_FILE),
        scopes=GMAIL_SCOPES,
        redirect_uri=GMAIL_REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    request.session["oauth_state"] = state
    return RedirectResponse(authorization_url)


@router.get("/auth/gmail/callback")
def gmail_callback(request: Request, code: str, db: Session = Depends(get_db)):
    """Google redirects here after consent; save token"""
    user_id = request.session.get("user_id")
    if not user_id:
        return {"error": "User not logged in"}

    flow = Flow.from_client_secrets_file(
        str(GMAIL_CLIENT_SECRET_FILE),
        scopes=GMAIL_SCOPES,
        redirect_uri=GMAIL_REDIRECT_URI
    )

    flow.fetch_token(code=code)
    credentials = flow.credentials

    # ✅ Get token as JSON string
    token_json = credentials.to_json()
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    # ✅ Save to database (persists on Render)
    user.gmail_token_json = token_json
    
    # ✅ Also save to file for local development (ephemeral on Render)
    token_path = get_token_path(user_id)
    try:
        with open(token_path, "w") as token_file:
            token_file.write(token_json)
        user.gmail_token_path = token_path
    except Exception as e:
        # If file write fails (e.g., on read-only filesystem), just skip
        print(f"Warning: Could not write token file: {e}")
        user.gmail_token_path = None
    
    db.commit()

    return RedirectResponse("/frontend/dashboard.html")