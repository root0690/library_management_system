"""
Authentication Service
Handles login, logout, password verification, and default admin creation.
"""

from database import execute_query, get_connection
from utils.hash_utils import hash_password, verify_password
from utils.validators import is_valid_username, is_valid_password, is_empty
from config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_ROLE
from datetime import datetime


def create_default_admin():
    """
    Create the default admin user if it does not exist.
    Returns True if created or already exists.
    """
    try:
        existing = execute_query(
            "SELECT UserID FROM users WHERE Username = %s",
            (DEFAULT_ADMIN_USERNAME,),
            fetchone=True
        )

        if existing:
            return True  # already exists

        password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)

        execute_query(
            """
            INSERT INTO users (Username, PasswordHash, Role)
            VALUES (%s, %s, %s)
            """,
            (DEFAULT_ADMIN_USERNAME, password_hash, DEFAULT_ADMIN_ROLE),
            commit=True
        )
        print(f"Default admin created → Username: {DEFAULT_ADMIN_USERNAME} | Password: {DEFAULT_ADMIN_PASSWORD}")
        return True

    except Exception as e:
        print(f"Error creating default admin: {e}")
        return False


def login(username: str, password: str):
    """
    Attempt to log in a user.
    Returns a dictionary with user info on success, or None on failure.
    """
    if is_empty(username) or is_empty(password):
        return None

    username = username.strip()

    try:
        user = execute_query(
            "SELECT UserID, Username, PasswordHash, Role FROM users WHERE Username = %s",
            (username,),
            fetchone=True
        )

        if not user:
            return None

        if not verify_password(password, user["PasswordHash"]):
            return None

        # Log the login action
        log_action(user["UserID"], f"User '{username}' logged in")

        return {
            "UserID": user["UserID"],
            "Username": user["Username"],
            "Role": user["Role"]
        }

    except Exception as e:
        print(f"Login error: {e}")
        return None


def log_action(user_id, action: str):
    """Write an entry to the auditlogs table."""
    try:
        execute_query(
            "INSERT INTO auditlogs (UserID, Action) VALUES (%s, %s)",
            (user_id, action),
            commit=True
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
            fetchone=True
        )
        if not user:
            return False

        if not verify_password(old_password, user["PasswordHash"]):
            return False

        new_hash = hash_password(new_password)
        execute_query(
            "UPDATE users SET PasswordHash = %s WHERE UserID = %s",
            (new_hash, user_id),
            commit=True
        )
        log_action(user_id, "Password changed")
        return True

    except Exception as e:
        print(f"Change password error: {e}")
        return False
