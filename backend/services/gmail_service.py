import base64
import os
import re
from email.message import EmailMessage
from typing import List, Dict
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from backend.config import GMAIL_SCOPES
from backend.models.email_log import EmailLog
from backend.services.sheets_service import (
    read_all_rows,
    mark_email_sent,  # ✅ Use the proper function
    mark_bounced,
    mark_replied,
)

# ======================================================
# GMAIL SERVICE
# ======================================================

def get_gmail_service(token_path: str):
    if not token_path or not os.path.exists(token_path):
        raise Exception("Gmail not connected for this user")

    creds = Credentials.from_authorized_user_file(
        token_path,
        GMAIL_SCOPES
    )

    return build("gmail", "v1", credentials=creds)


# ======================================================
# SEND EMAIL
# ======================================================

def send_email(
    db: Session,
    user,
    sheet_id: str,
    to_email: str,
    subject: str,
    body: str,
    row_number: int,
    followup_count: int  # ✅ This should be the NEW count (already incremented in scheduler)
):
    """
    Send an email via Gmail API.
    
    Args:
        followup_count: The NEW followup count (1, 2, 3, 4, or 5) AFTER this email is sent
    """
    service = get_gmail_service(user.gmail_token_path)

    message = EmailMessage()
    message["To"] = to_email
    message["From"] = "me"
    message["Subject"] = subject
    
    # ✅ Include resume link in email body (not as attachment)
    full_body = body
    if user.resume_link:  # Assuming you store resume link in User model
        full_body += f"\n\nResume: {user.resume_link}"
    
    message.set_content(full_body)

    # ❌ REMOVED: Fixed resume attachment
    # If you want to support file attachments later, you can add per-user file storage

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    try:
        response = service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()

        # ✅ Update Google Sheet properly (includes Next_Send_Date calculation)
        mark_email_sent(sheet_id, row_number, followup_count)

        # ✅ Log to database
        log = EmailLog(
            user_id=user.id,
            to_email=to_email,
            status=f"FOLLOWUP_{followup_count}" if followup_count > 1 else "SENT",
            sent_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()

        return response.get("threadId")

    except HttpError as e:
        error_msg = str(e)
        
        # ✅ Check if it's a bounce error (invalid email)
        if any(keyword in error_msg.lower() for keyword in [
            "address not found",
            "user unknown",
            "does not exist",
            "invalid recipient",
            "recipient address rejected"
        ]):
            mark_bounced(sheet_id, row_number, error_msg)
            
            log = EmailLog(
                user_id=user.id,
                to_email=to_email,
                status="BOUNCED",
                error=error_msg,
                sent_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
        
        raise


# ======================================================
# CHECK REPLIES (Run Once Daily)
# ======================================================

def check_replies(
    db: Session,
    user,
    sheet_id: str
):
    """
    Check for replies to ALL previously sent emails.
    Should be run once per day as a separate scheduled task.
    
    This function:
    1. Reads all rows from the sheet
    2. Finds emails that were sent but haven't replied yet
    3. Checks their Gmail threads for replies
    4. Marks them as replied if found
    """
    service = get_gmail_service(user.gmail_token_path)
    rows = read_all_rows(sheet_id)

    for row_index, row in enumerate(rows, start=2):
        if len(row) < 9:
            continue

        email = row[0] if len(row) > 0 else ""
        replied = row[4] if len(row) > 4 else ""
        bounced = row[5] if len(row) > 5 else ""
        followup_count = int(row[6]) if len(row) > 6 and row[6] else 0
        last_sent_date = row[7] if len(row) > 7 else ""

        # Skip if:
        # - No email address
        # - Already replied
        # - Bounced
        # - Never sent (followup_count = 0)
        if not email or replied == "TRUE" or bounced == "TRUE" or followup_count == 0:
            continue

        # ✅ Search for emails sent to this address
        try:
            # Search for messages TO this email address
            results = service.users().messages().list(
                userId="me",
                q=f"to:{email}"
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                continue

            # Check the most recent thread
            latest_msg = messages[0]
            thread_id = latest_msg["threadId"]

            # Get the full thread
            thread = service.users().threads().get(
                userId="me",
                id=thread_id
            ).execute()

            thread_messages = thread.get("messages", [])

            # ✅ If thread has more than 1 message, there might be a reply
            if len(thread_messages) > 1:
                # Check messages after the first one
                for msg in thread_messages[1:]:
                    headers = msg.get("payload", {}).get("headers", [])
                    from_header = next(
                        (h["value"] for h in headers if h["name"].lower() == "from"),
                        ""
                    )

                    # ✅ If the reply is FROM the recipient (not from us)
                    if email.lower() in from_header.lower():
                        mark_replied(sheet_id, row_index)

                        db.add(
                            EmailLog(
                                user_id=user.id,
                                to_email=email,
                                status="REPLIED",
                                sent_at=datetime.utcnow()
                            )
                        )
                        db.commit()
                        break

        except HttpError as e:
            # If there's an error checking this email, just continue
            continue


# ======================================================
# CHECK BOUNCES (Run Periodically)
# ======================================================

def check_bounces(
    db: Session,
    user,
    sheet_id: str
):
    """
    Check for bounced emails from the last 24 hours.
    Bounces are usually delivered as mailer-daemon messages.
    """
    service = get_gmail_service(user.gmail_token_path)

    # ✅ Only check bounces from the last 24 hours
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y/%m/%d")
    
    try:
        results = service.users().messages().list(
            userId="me",
            q=f"from:mailer-daemon OR subject:'Delivery Status Notification' after:{yesterday}"
        ).execute()
    except HttpError:
        return

    rows = read_all_rows(sheet_id)

    for msg in results.get("messages", []):
        try:
            message = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()
        except HttpError:
            continue

        payload = message.get("payload", {})
        body = ""

        # ✅ Extract body from all parts
        if "parts" in payload:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        body += base64.urlsafe_b64decode(data).decode(errors="ignore")
        else:
            # Single-part message
            data = payload.get("body", {}).get("data")
            if data:
                body = base64.urlsafe_b64decode(data).decode(errors="ignore")

        # ✅ Extract bounced email address from body
        match = re.search(
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,})',
            body
        )

        if not match:
            continue

        bounced_email = match.group(1).lower()

        # ✅ Find the bounced email in the sheet
        for idx, row in enumerate(rows, start=2):
            if row and len(row) > 0 and row[0].lower() == bounced_email:
                mark_bounced(sheet_id, idx, "Mail bounced (mailer-daemon)")

                db.add(
                    EmailLog(
                        user_id=user.id,
                        to_email=bounced_email,
                        status="BOUNCED",
                        error="Mail bounced",
                        sent_at=datetime.utcnow()
                    )
                )
                db.commit()
                break