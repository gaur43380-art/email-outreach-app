#gate_auth.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, FileResponse

from backend.config import WEBSITE_ACCESS_ID, WEBSITE_ACCESS_PASSWORD

router = APIRouter()


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def gate_passed(request: Request) -> bool:
    return bool(request.session.get("gate_passed"))


def require_gate(request: Request):
    """
    Can be used inside routes to block access
    """
    if not gate_passed(request):
        return RedirectResponse("/frontend/gate.html", status_code=302)


# -------------------------------------------------
# Routes
# -------------------------------------------------

@router.get("/gate")
def gate_page():
    """
    Serve gate HTML page
    """
    return FileResponse("frontend/gate.html")


@router.post("/gate/login")
def gate_login(
    request: Request,
    access_id: str = Form(...),
    password: str = Form(...)
):
    """
    Validate fixed gate credentials
    """
    if access_id != WEBSITE_ACCESS_ID or password != WEBSITE_ACCESS_PASSWORD:
        return FileResponse("frontend/gate.html", status_code=401)

    # Mark gate as passed
    request.session["gate_passed"] = True

    # Redirect to normal app entry
    return RedirectResponse("/frontend/index.html", status_code=302)


@router.get("/gate/logout")
def gate_logout(request: Request):
    """
    Clears gate session
    """
    request.session.pop("gate_passed", None)
    return RedirectResponse("/frontend/gate.html", status_code=302)
