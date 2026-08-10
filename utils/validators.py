"""
Input validation helpers.
"""

import re


def is_empty(value) -> bool:
    """Return True if value is None or empty/whitespace string."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def is_valid_username(username: str) -> bool:
    """Username: 3-30 characters, letters, numbers, underscore."""
    if is_empty(username):
        return False
    return bool(re.match(r"^[A-Za-z0-9_]{3,30}$", username.strip()))


def is_valid_password(password: str) -> bool:
    """Password must be at least 6 characters."""
    if is_empty(password):
        return False
    return len(password) >= 6


def is_valid_isbn(isbn: str) -> bool:
    """Basic ISBN check (allows empty for optional field)."""
    if is_empty(isbn):
        return True  # optional
    cleaned = isbn.replace("-", "").replace(" ", "")
    return cleaned.isdigit() and len(cleaned) in (10, 13)


def is_positive_integer(value) -> bool:
    """Check if value can be converted to a positive integer (>= 0)."""
    try:
        num = int(value)
        return num >= 0
    except (TypeError, ValueError):
        return False


def is_valid_phone(phone: str) -> bool:
    """Very basic phone validation (optional field)."""
    if is_empty(phone):
        return True
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def sanitize_string(value: str) -> str:
    """Strip whitespace from a string."""
    if value is None:
        return ""
    return str(value).strip()
