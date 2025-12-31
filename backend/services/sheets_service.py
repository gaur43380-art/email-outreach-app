from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import List

from backend.config import (
    SHEETS_SERVICE_ACCOUNT_FILE,
    DEFAULT_SHEET_NAME
)
from backend.utils.date_utils import (
    calculate_next_send_date,
    get_status_from_followup_count,
    parse_date
)

# ======================================================
# SCOPES
# ======================================================

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# ======================================================
# SERVICE CREATOR
# ======================================================

def get_sheets_service():
    creds = Credentials.from_service_account_file(
        SHEETS_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


# ======================================================
# READ OPERATIONS
# ======================================================

def read_all_rows(sheet_id: str, sheet_name: str = DEFAULT_SHEET_NAME) -> List[list]:
    """
    Reads all data rows (excluding header)
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{sheet_name}!A2:Z"
    ).execute()

    return result.get("values", [])


# ======================================================
# WRITE OPERATIONS
# ======================================================

def update_cell(
    sheet_id: str,
    row_number: int,
    column_letter: str,
    value,
    sheet_name: str = DEFAULT_SHEET_NAME
):
    service = get_sheets_service()
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{sheet_name}!{column_letter}{row_number}",
        valueInputOption="RAW",
        body={"values": [[value]]}
    ).execute()


# ======================================================
# COMMON HELPERS
# ======================================================

def mark_email_sent(
    sheet_id: str,
    row_number: int,
    new_followup_count: int,  # ✅ This should be the NEW count (incremented)
    sheet_name: str = DEFAULT_SHEET_NAME
):
    """
    Update sheet after successfully sending an email.
    
    Updates:
    - Column D (Status): Based on followup count
    - Column G (Followup_Count): Increment to new count
    - Column H (Last_Sent_Date): Today's date
    - Column I (Next_Send_Date): Calculated based on followup sequence
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    today_date = parse_date(today_str)
    
    # Calculate next send date based on the NEW followup count
    next_send_date = calculate_next_send_date(new_followup_count, today_date)
    
    # Get appropriate status
    status = get_status_from_followup_count(new_followup_count)
    
    # Update all columns
    update_cell(sheet_id, row_number, "D", status, sheet_name)              # Status
    update_cell(sheet_id, row_number, "G", new_followup_count, sheet_name)  # Followup_Count
    update_cell(sheet_id, row_number, "H", today_str, sheet_name)           # Last_Sent_Date
    update_cell(sheet_id, row_number, "I", next_send_date, sheet_name)      # Next_Send_Date ✅ CRITICAL!


def mark_bounced(
    sheet_id: str,
    row_number: int,
    error_msg: str,
    sheet_name: str = DEFAULT_SHEET_NAME
):
    update_cell(sheet_id, row_number, "F", "TRUE", sheet_name)          # Bounce
    update_cell(sheet_id, row_number, "K", error_msg, sheet_name)       # Last_Error


def mark_replied(
    sheet_id: str,
    row_number: int,
    sheet_name: str = DEFAULT_SHEET_NAME
):
    update_cell(sheet_id, row_number, "E", "TRUE", sheet_name)          # Replied