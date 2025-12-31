from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.email_log import EmailLog
from backend.auth.website_auth import login_required

router = APIRouter(prefix="/logs")


@router.get("/my")
def my_logs(request: Request, db: Session = Depends(get_db)):
    if not login_required(request):
        raise HTTPException(status_code=401, detail="Not logged in")

    user_id = request.session.get("user_id")
    
    logs = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user_id)
        .order_by(EmailLog.sent_at.desc())
        .limit(200)
        .all()
    )

    return [
        {
            "email": l.to_email,
            "status": l.status,
            "time": l.sent_at.strftime("%Y-%m-%d %H:%M:%S") if l.sent_at else None,
            "error": l.error
        }
        for l in logs
    ]