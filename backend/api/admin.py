from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.user import User
from backend.auth.website_auth import admin_required

router = APIRouter(prefix="/admin")


@router.get("/users")
def get_all_users(request: Request, db: Session = Depends(get_db)):
    if not admin_required(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    users = db.query(User).all()

    return JSONResponse(content=[
        {
            "id": u.id,
            "email": u.email,
            "is_paused": u.is_paused,
            "sheet_id": u.sheet_id,
            "gmail_connected": bool(u.gmail_token_path),
            "resume_link": u.resume_link
        } for u in users
    ])


@router.post("/pause/{user_id}")
def pause_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    if not admin_required(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_paused = True
    db.commit()
    return {"status": "paused"}


@router.post("/resume/{user_id}")
def resume_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    if not admin_required(request):
        raise HTTPException(status_code=403, detail="Unauthorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_paused = False
    db.commit()
    return {"status": "active"}