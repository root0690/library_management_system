"""
Date helper functions.
"""

from datetime import datetime, date, timedelta
from config import DEFAULT_LOAN_DAYS


def _to_date(value):
    """Convert str / date / datetime to a date object."""
    if value is None:
        raise ValueError("Date value is empty")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    if " " in s:
        s = s.split(" ")[0]
    return datetime.strptime(s, "%Y-%m-%d").date()


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_due_date(issue_date=None, days: int = None) -> str:
    if days is None:
        days = DEFAULT_LOAN_DAYS
    if issue_date is None:
        base = datetime.now().date()
    else:
        base = _to_date(issue_date)
    due = base + timedelta(days=days)
    return due.strftime("%Y-%m-%d")


def days_between(start_date, end_date) -> int:
    """Accepts str, date, or datetime."""
    d1 = _to_date(start_date)
    d2 = _to_date(end_date)
    return (d2 - d1).days


def is_overdue(due_date, return_date=None) -> bool:
    check_date = return_date if return_date else today_str()
    return days_between(due_date, check_date) > 0
