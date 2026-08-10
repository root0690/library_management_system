"""
Date helper functions.
"""

from datetime import datetime, timedelta
from config import DEFAULT_LOAN_DAYS


def today_str() -> str:
    """Return today's date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    """Return current datetime as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_due_date(issue_date: str = None, days: int = None) -> str:
    """
    Calculate due date from issue date + loan days.
    issue_date should be YYYY-MM-DD. If None, uses today.
    """
    if days is None:
        days = DEFAULT_LOAN_DAYS
    if issue_date is None:
        base = datetime.now()
    else:
        base = datetime.strptime(issue_date, "%Y-%m-%d")
    due = base + timedelta(days=days)
    return due.strftime("%Y-%m-%d")


def days_between(start_date: str, end_date: str) -> int:
    """
    Return number of days between two YYYY-MM-DD dates.
    Positive if end_date is after start_date.
    """
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    return (d2 - d1).days


def is_overdue(due_date: str, return_date: str = None) -> bool:
    """Check if a book is overdue."""
    check_date = return_date if return_date else today_str()
    return days_between(due_date, check_date) > 0
