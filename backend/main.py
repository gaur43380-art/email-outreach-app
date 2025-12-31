from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware  # ✅ FIXED: starlette not starlettes
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
import threading
from apscheduler.schedulers.background import BackgroundScheduler

# -------------------------------------------------
# Core
# -------------------------------------------------
from backend.config import SECRET_KEY
from backend.db.database import engine, Base

# -------------------------------------------------
# Routers
# -------------------------------------------------
from backend.auth.gate_auth import router as gate_router
from backend.auth.website_auth import router as website_auth_router
from backend.auth.gmail_oauth import router as gmail_router

from backend.api import logs, admin, user_settings, templates  # ✅ Added templates

# -------------------------------------------------
# Background workers
# -------------------------------------------------
from backend.workers.scheduler import scheduler_loop, check_all_replies_daily

# =================================================
# APP INIT
# =================================================

app = FastAPI(title="Email Outreach App")

# =================================================
# SESSION
# =================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=2 * 24 * 60 * 60,  # 2 days
)

# =================================================
# GATE ROUTES (PUBLIC)
# =================================================

app.include_router(gate_router)

# =================================================
# AUTH + API ROUTES (AFTER GATE)
# =================================================

app.include_router(website_auth_router)
app.include_router(gmail_router)
app.include_router(templates.router)  # ✅ Added templates router
app.include_router(logs.router)
app.include_router(admin.router)
app.include_router(user_settings.router)

# =================================================
# STATIC FILES (CSS / JS ONLY)
# =================================================

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# =================================================
# ROOT ENTRY POINT (STRICT GATE)
# =================================================

@app.get("/", include_in_schema=False)
def root(request: Request):
    if not request.session.get("gate_passed"):
        return RedirectResponse("/gate", status_code=302)

    return FileResponse("frontend/index.html")

# =================================================
# STARTUP
# =================================================

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start main sending loop (continuous)
    threading.Thread(target=scheduler_loop, daemon=True).start()
    
    # Start daily reply checker (runs once per day at 2 AM)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_all_replies_daily,
        'cron',
        hour=2,  # Run at 2 AM every day
        minute=0
    )
    scheduler.start()

# =================================================
# HEALTH
# =================================================

@app.get("/health")
def health():
    return {"status": "ok"}