"""
Fine Service - Calculate overdue fines
"""

from utils.date_utils import days_between, today_str
from config import DEFAULT_FINE_RATE


def calculate_fine(due_date, return_date=None, fine_rate=None) -> float:
    """
    Fine = Overdue Days x Daily Fine Rate
    Accepts str/date/datetime for due_date and return_date.
    """
    if fine_rate is None:
        fine_rate = DEFAULT_FINE_RATE

    check_date = return_date if return_date else today_str()
    try:
        overdue_days = days_between(due_date, check_date)
    except Exception:
        return 0.0

    if overdue_days <= 0:
        return 0.0

    return round(overdue_days * float(fine_rate), 2)


def get_overdue_days(due_date, return_date=None) -> int:
    check_date = return_date if return_date else today_str()
    try:
        days = days_between(due_date, check_date)
        return max(0, days)
    except Exception:
        return 0
