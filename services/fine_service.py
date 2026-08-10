"""
Fine Service - Calculate overdue fines
"""

from utils.date_utils import days_between, today_str
from config import DEFAULT_FINE_RATE


def calculate_fine(due_date: str, return_date: str = None, fine_rate: float = None) -> float:
    """
    Fine = Overdue Days × Daily Fine Rate
    Returns 0 if not overdue.
    """
    if fine_rate is None:
        fine_rate = DEFAULT_FINE_RATE

    check_date = return_date if return_date else today_str()
    overdue_days = days_between(due_date, check_date)

    if overdue_days <= 0:
        return 0.0

    return round(overdue_days * float(fine_rate), 2)


def get_overdue_days(due_date: str, return_date: str = None) -> int:
    check_date = return_date if return_date else today_str()
    days = days_between(due_date, check_date)
    return max(0, days)
