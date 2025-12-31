from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# Password helpers
# -----------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password[:72], hashed)

# -----------------------------
# Session / Auth helpers
# -----------------------------

def login_user(request: Request, user: User):
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["is_admin"] = user.is_admin

def logout_user(request: Request):
    request.session.clear()

def login_required(request: Request) -> bool:
    return bool(request.session.get("user_id"))

def admin_required(request: Request) -> bool:
    return bool(
        request.session.get("user_id") and request.session.get("is_admin")
    )

# -----------------------------
# Routes
# -----------------------------

@router.post("/signup")
def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    resume_link: str = Form(None),
    sheet_id: str = Form(None),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return HTMLResponse("User already exists", status_code=400)

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_admin=False,
        is_paused=False,
        resume_link=resume_link,
        sheet_id=sheet_id
    )
    db.add(user)
    db.commit()

    login_user(request, user)
    return RedirectResponse("/frontend/dashboard.html", status_code=302)


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return HTMLResponse("Invalid credentials", status_code=401)

    login_user(request, user)
    return RedirectResponse("/frontend/dashboard.html", status_code=302)


@router.get("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/frontend/index.html", status_code=302)


@router.get("/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    if not login_required(request):
        return {"authenticated": False}

    user = db.query(User).filter(User.id == request.session["user_id"]).first()

    if not user:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "resume_link": user.resume_link,
        "sheet_id": user.sheet_id,
        "email_subject": user.email_subject,
        "gmail_connected": bool(user.gmail_token_path),
        "is_paused": user.is_paused
    }