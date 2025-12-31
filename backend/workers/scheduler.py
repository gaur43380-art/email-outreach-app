# backend/workers/scheduler.py

import time
import random
from datetime import datetime, date

from backend.db.database import SessionLocal  # ✅ Import SessionLocal directly
from backend.models.user import User

from backend.services.sheets_service import read_all_rows
from backend.services.gmail_service import (
    send_email,
    check_replies,
    check_bounces
)
from backend.utils.template_engine import render_template
from backend.config import (
    MAX_EMAILS_PER_DAY,
    MIN_DELAY_SECONDS,
    MAX_DELAY_SECONDS
)

# ======================================================
# Scheduler Helpers
# ======================================================

def daily_send_count(db, user_id):
    from backend.models.email_log import EmailLog
    today = date.today()
    return db.query(EmailLog).filter(
        EmailLog.user_id == user_id,
        EmailLog.sent_at >= today
    ).count()


# ======================================================
# Per-user Scheduler
# ======================================================

def run_scheduler_for_user(db, user):
    if not user.sheet_id:
        return

    sheet_id = user.sheet_id

    # 1️⃣ Check bounces first
    try:
        check_bounces(db, user, sheet_id)
    except Exception as e:
        print(f"Error checking bounces for {user.email}: {e}")

    try:
        rows = read_all_rows(sheet_id)
    except Exception as e:
        print(f"Error reading sheet for {user.email}: {e}")
        return

    for row_index, row in enumerate(rows, start=2):

        # Gmail daily safety
        if daily_send_count(db, user.id) >= MAX_EMAILS_PER_DAY:
            return

        email = row[0] if len(row) > 0 else ""
        name = row[1] if len(row) > 1 else ""
        company = row[2] if len(row) > 2 else ""
        replied = row[4] if len(row) > 4 else ""
        bounced = row[5] if len(row) > 5 else ""
        
        # Get CURRENT followup count from sheet
        current_followup_count = int(row[6]) if len(row) > 6 and row[6] else 0
        
        next_send = row[8] if len(row) > 8 else ""

        # Stop conditions
        if not email:
            continue
        if replied == "TRUE" or bounced == "TRUE":
            continue
        
        # Stop if already sent 5 emails
        if current_followup_count >= 5:
            continue

        # Respect scheduled date
        if next_send:
            try:
                if datetime.strptime(next_send, "%Y-%m-%d").date() > date.today():
                    continue
            except ValueError:
                pass

        # Choose template based on followup count
        if current_followup_count == 0:
            # Initial email
            template = user.email_template or "Hi {Name},\n\nBest regards,\n{MyName}"
        else:
            # Follow-up emails (use followup template if available, else use initial)
            template = user.followup_template or user.email_template or "Hi {Name},\n\nBest regards,\n{MyName}"

        # Use user's custom subject or default
        subject = user.email_subject or "Application / Follow-up"

        # Proper placeholder replacement
        email_body = render_template(template, {
            "Name": name or "Hiring Manager",
            "Company": company or "",
            "MyName": user.full_name or user.email,
            "ResumeLink": user.resume_link or "",
            # Alternative placeholder formats
            "My Name": user.full_name or user.email,
            "company": company or "",
            "Resume Link": user.resume_link or ""
        })

        # Calculate NEW followup count (increment before sending)
        new_followup_count = current_followup_count + 1

        try:
            thread_id = send_email(
                db=db,
                user=user,
                sheet_id=sheet_id,
                to_email=email,
                subject=subject,
                body=email_body,
                row_number=row_index,
                followup_count=new_followup_count
            )

            # Human-like delay
            time.sleep(random.randint(
                MIN_DELAY_SECONDS,
                MAX_DELAY_SECONDS
            ))

        except Exception as e:
            print(f"Error sending to {email}: {e}")
            continue


# ======================================================
# Reply Checker (Separate Function - Run Once Daily)
# ======================================================

def check_all_replies_daily():
    """
    Separate task that runs once per day to check for replies.
    """
    db = SessionLocal()  # ✅ Create session properly
    try:
        users = db.query(User).all()

        for user in users:
            if not user.sheet_id:
                continue
            
            try:
                check_replies(db, user, user.sheet_id)
            except Exception as e:
                print(f"Error checking replies for {user.email}: {e}")
    finally:
        db.close()  # ✅ Always close session


# ======================================================
# Main Loop
# ======================================================

def scheduler_loop():
    """
    Main sending loop - checks continuously for emails to send.
    """
    while True:
        db = SessionLocal()  # ✅ Create new session for each iteration
        try:
            users = db.query(User).all()

            for user in users:
                if user.is_paused:
                    continue

                try:
                    run_scheduler_for_user(db, user)
                except Exception as e:
                    print(f"Scheduler error for {user.email}: {e}")
        finally:
            db.close()  # ✅ Always close session

        time.sleep(60)  # Check every minute