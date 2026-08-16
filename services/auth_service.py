"""
Authentication Service
Handles login (online + offline), logout, password verification, default admin.
"""

import json
import os

from database import execute_query
from utils.hash_utils import hash_password, verify_password
from utils.validators import is_valid_password, is_empty
from config import (
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_ROLE,
    BASE_DIR,
)

OFFLINE_CACHE_PATH = os.path.join(BASE_DIR, "database", "offline_users.json")


def _load_offline_cache():
    """Load locally cached users for offline login."""
    try:
        if os.path.exists(OFFLINE_CACHE_PATH):
            with open(OFFLINE_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_offline_cache(cache: dict):
    try:
        os.makedirs(os.path.dirname(OFFLINE_CACHE_PATH), exist_ok=True)
        with open(OFFLINE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Could not save offline cache: {e}")


def _cache_user_for_offline(username: str, password_hash: str, role: str, user_id: int):
    """Remember a user so they can log in when MySQL is offline."""
    cache = _load_offline_cache()
    cache[username.lower()] = {
        "Username": username,
        "PasswordHash": password_hash,
        "Role": role,
        "UserID": user_id,
    }
    # Always keep default admin entry usable offline
    _save_offline_cache(cache)


def create_default_admin():
    """Create the default admin user if it does not exist (requires MySQL)."""
    try:
        existing = execute_query(
            "SELECT UserID FROM users WHERE Username = %s",
            (DEFAULT_ADMIN_USERNAME,),
            fetchone=True,
        )
        if existing:
            return True

        password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
        execute_query(
            """
            INSERT INTO users (Username, PasswordHash, Role)
            VALUES (%s, %s, %s)
            """,
            (DEFAULT_ADMIN_USERNAME, password_hash, DEFAULT_ADMIN_ROLE),
            commit=True,
        )
        print(
            f"Default admin created → Username: {DEFAULT_ADMIN_USERNAME} | "
            f"Password: {DEFAULT_ADMIN_PASSWORD}"
        )
        return True
    except Exception as e:
        print(f"Error creating default admin: {e}")
        return False


def _offline_login(username: str, password: str):
    """
    Authenticate without MySQL.
    1) Check local offline cache (users who logged in before while online)
    2) Fall back to default admin credentials from config
    """
    username = username.strip()
    cache = _load_offline_cache()
    key = username.lower()

    if key in cache:
        entry = cache[key]
        if verify_password(password, entry.get("PasswordHash", "")):
            return {
                "UserID": entry.get("UserID", 0),
                "Username": entry.get("Username", username),
                "Role": entry.get("Role", "Administrator"),
                "Offline": True,
            }

    # Built-in offline emergency login (works even with empty cache)
    allowed_names = {DEFAULT_ADMIN_USERNAME.lower(), "admin", "root"}
    if username.lower() in allowed_names and password == DEFAULT_ADMIN_PASSWORD:
        return {
            "UserID": 0,
            "Username": username,
            "Role": DEFAULT_ADMIN_ROLE,
            "Offline": True,
        }

    return None


def login(username: str, password: str):
    """
    Attempt to log in a user.
    - Tries MySQL first (online)
    - If server is unreachable, falls back to offline login
    Returns user dict on success, or None on failure.
    User dict may include Offline=True when logged in without MySQL.
    """
    if is_empty(username) or is_empty(password):
        return None

    username = username.strip()

    # --- Online path ---
    try:
        user = execute_query(
            "SELECT UserID, Username, PasswordHash, Role FROM users WHERE Username = %s",
            (username,),
            fetchone=True,
        )

        if not user:
            return None

        if not verify_password(password, user["PasswordHash"]):
            return None

        # Cache for future offline use
        _cache_user_for_offline(
            user["Username"], user["PasswordHash"], user["Role"], user["UserID"]
        )

        try:
            log_action(user["UserID"], f"User '{username}' logged in")
        except Exception:
            pass

        return {
            "UserID": user["UserID"],
            "Username": user["Username"],
            "Role": user["Role"],
            "Offline": False,
        }

    except Exception as e:
        # Server down / connection refused / access denied → offline mode
        print(f"Online login failed ({e}). Trying offline login...")
        offline_user = _offline_login(username, password)
        if offline_user:
            print(f"Offline login successful for '{username}'")
            return offline_user
        print(f"Offline login failed for '{username}'")
        return None


def log_action(user_id, action: str):
    """Write an entry to the auditlogs table (no-op if offline)."""
    try:
        execute_query(
            "INSERT INTO auditlogs (UserID, Action) VALUES (%s, %s)",
            (user_id, action),
            commit=True,
        )
    except Exception as e:
        print(f"Failed to write audit log: {e}")


def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    """Change a user's password after verifying the old one."""
    if not is_valid_password(new_password):
        return False

    try:
        user = execute_query(
            "SELECT PasswordHash FROM users WHERE UserID = %s",
            (user_id,),
            fetchone=True,
        )
        if not user:
            return False

        if not verify_password(old_password, user["PasswordHash"]):
            return False

        new_hash = hash_password(new_password)
        execute_query(
            "UPDATE users SET PasswordHash = %s WHERE UserID = %s",
            (new_hash, user_id),
            commit=True,
        )
        log_action(user_id, "Password changed")
        return True
    except Exception as e:
        print(f"Change password error: {e}")
        return False
