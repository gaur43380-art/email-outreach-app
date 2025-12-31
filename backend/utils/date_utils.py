# backend/utils/date_utils.py

from datetime import datetime, date, timedelta

def today() -> date:
    """Return current date (without time)."""
    return datetime.utcnow().date()

def now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()

def add_days(base_date: date, days: int) -> date:
    """Return a new date by adding days to base_date."""
    return base_date + timedelta(days=days)

def days_between(start_date: date, end_date: date) -> int:
    """Return number of days between two dates."""
    return (end_date - start_date).days

def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    """Return date as formatted string."""
    return d.strftime(fmt)

def parse_date(date_str: str, fmt: str = "%Y-%m-%d") -> date:
    """Convert a string to a date object."""
    return datetime.strptime(date_str, fmt).date()

def is_today(d: date) -> bool:
    """Check if the given date is today."""
    return d == today()

def is_past(d: date) -> bool:
    """Check if the given date is before today."""
    return d < today()

def is_future(d: date) -> bool:
    """Check if the given date is after today."""
    return d > today()


# ✅ NEW FUNCTION - CRITICAL FOR YOUR EMAIL FLOW
def calculate_next_send_date(current_followup_count: int, last_sent_date: date) -> str:
    """
    Calculate next send date based on email sequence:
    
    Email Flow:
    - Email 0 (Initial) → Email 1 (Follow-up #1): +7 days
    - Email 1 (Follow-up #1) → Email 2 (Follow-up #2): +7 days
    - Email 2 (Follow-up #2) → Email 3 (Retry #1): +60 days
    - Email 3 (Retry #1) → Email 4 (Retry #2): +60 days
    - Email 4 (Retry #2) → Permanently rejected
    
    Args:
        current_followup_count: The count AFTER this email is sent (1, 2, 3, 4, or 5)
        last_sent_date: The date this email was just sent
    
    Returns:
        Next send date as string "YYYY-MM-DD" or empty string if no more emails
    """
    if current_followup_count == 1:
        # Just sent initial email → schedule follow-up #1 in 7 days
        return format_date(add_days(last_sent_date, 7))
    
    elif current_followup_count == 2:
        # Just sent follow-up #1 → schedule follow-up #2 in 7 days
        return format_date(add_days(last_sent_date, 7))
    
    elif current_followup_count == 3:
        # Just sent follow-up #2 → schedule retry #1 in 60 days
        return format_date(add_days(last_sent_date, 60))
    
    elif current_followup_count == 4:
        # Just sent retry #1 → schedule retry #2 in 60 days
        return format_date(add_days(last_sent_date, 60))
    
    else:
        # Sent 5 emails total → permanently rejected, no more emails
        return ""


def get_status_from_followup_count(followup_count: int) -> str:
    """
    Return appropriate status based on followup count.
    
    Status progression:
    0 → "Pending" (not sent yet)
    1 → "Sent" (initial email sent)
    2 → "Follow-up-1" (first follow-up sent)
    3 → "Follow-up-2" (second follow-up sent, waiting 60 days)
    4 → "Retry-1" (first retry sent, waiting 60 days)
    5 → "Permanently-Rejected" (all attempts exhausted)
    """
    status_map = {
        0: "Pending",
        1: "Sent",
        2: "Follow-up-1",
        3: "Follow-up-2",
        4: "Retry-1",
        5: "Permanently-Rejected"
    }
    return status_map.get(followup_count, "Unknown")