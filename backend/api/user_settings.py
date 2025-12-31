from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.user import User

router = APIRouter(prefix="/user")


# -------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------

class UpdateSettingsRequest(BaseModel):
    full_name: Optional[str] = None
    resume_link: Optional[str] = None
    sheet_id: Optional[str] = None
    email_template: Optional[str] = None
    followup_template: Optional[str] = None
    email_subject: Optional[str] = None


# -------------------------------------------------
# GET USER SETTINGS
# -------------------------------------------------

@router.get("/settings")
def get_user_settings(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    return {
        "email": user.email,
        "full_name": user.full_name,
        "resume_link": user.resume_link,
        "sheet_id": user.sheet_id,
        "email_template": user.email_template,
        "followup_template": user.followup_template,
        "email_subject": user.email_subject,
        "gmail_connected": bool(user.gmail_token_path),
        "is_paused": user.is_paused
    }


# -------------------------------------------------
# UPDATE USER SETTINGS
# -------------------------------------------------

@router.post("/settings")
def update_user_settings(
    request: Request,
    settings: UpdateSettingsRequest,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    # Update only provided fields
    if settings.full_name is not None:
        user.full_name = settings.full_name
    
    if settings.resume_link is not None:
        user.resume_link = settings.resume_link
    
    if settings.sheet_id is not None:
        user.sheet_id = settings.sheet_id
    
    if settings.email_template is not None:
        user.email_template = settings.email_template
    
    if settings.followup_template is not None:
        user.followup_template = settings.followup_template
    
    if settings.email_subject is not None:
        user.email_subject = settings.email_subject

    db.commit()

    return {
        "status": "success",
        "message": "Settings updated successfully"
    }


# -------------------------------------------------
# START SENDING
# -------------------------------------------------

@router.post("/start")
def start_sending(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    if user.is_paused:
        return JSONResponse(
            {"error": "User is paused. Resume first."},
            status_code=400
        )

    if not user.gmail_token_path:
        return JSONResponse(
            {"error": "Gmail not connected"},
            status_code=400
        )

    if not user.sheet_id:
        return JSONResponse(
            {"error": "Google Sheet not linked"},
            status_code=400
        )
    
    if not user.resume_link:
        return JSONResponse(
            {"error": "Resume link not provided"},
            status_code=400
        )
    
    if not user.full_name:
        return JSONResponse(
            {"error": "Your name not provided"},
            status_code=400
        )
    
    if not user.email_template:
        return JSONResponse(
            {"error": "Email template not set"},
            status_code=400
        )

    # Nothing else to do — scheduler will pick this user
    return {
        "status": "sending_started",
        "message": "Scheduler will now process emails"
    }


# -------------------------------------------------
# PAUSE SENDING
# -------------------------------------------------

@router.post("/pause")
def pause_sending(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    user.is_paused = True
    db.commit()

    return {"status": "paused"}


# -------------------------------------------------
# RESUME SENDING
# -------------------------------------------------

@router.post("/resume")
def resume_sending(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    user.is_paused = False
    db.commit()

    return {"status": "resumed"}