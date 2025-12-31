# backend/api/templates.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.db.database import get_db
from backend.models.user import User

router = APIRouter(prefix="/templates")


# -------------------------------------------------
# REQUEST MODEL
# -------------------------------------------------

class TemplateRequest(BaseModel):
    template: str  # Single template for all emails


# -------------------------------------------------
# SAVE TEMPLATE
# -------------------------------------------------

@router.post("/save")
async def save_template(request: Request, data: TemplateRequest):
    """
    Save email template for logged-in user.
    This ONE template will be used for initial email and ALL follow-ups.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    # Save template to database
    user.email_template = data.template
    db.commit()

    return {"status": "template_saved"}


# -------------------------------------------------
# LOAD TEMPLATE
# -------------------------------------------------

@router.get("/load")
def load_template(request: Request):
    """
    Load email template for logged-in user.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    # Return template from database (or default if empty)
    default_template = """Hi {Name},

I hope this email finds you well. I am reaching out regarding opportunities at {Company}.

[Add your message here]

You can view my resume here: {ResumeLink}

Best regards,
{MyName}"""

    return {
        "template": user.email_template or default_template
    }