"""
User Service - Manage system users (Admin / Librarian)
"""

from database import execute_query
from utils.hash_utils import hash_password, verify_password
from utils.validators import is_empty, is_valid_username, is_valid_password, sanitize_string
from services.auth_service import log_action


def get_all_users():
    return execute_query(
        "SELECT UserID, Username, Role, CreatedAt FROM users ORDER BY UserID",
        fetchall=True
    ) or []


def get_user_by_id(user_id: int):
    return execute_query(
        "SELECT UserID, Username, Role, CreatedAt FROM users WHERE UserID = %s",
        (user_id,),
        fetchone=True
    )


def add_user(username: str, password: str, role: str, current_user_id=None):
    username = sanitize_string(username)
    role = sanitize_string(role)

    if not is_valid_username(username):
        return False, "Username must be 3-30 characters (letters, numbers, underscore)."

    if not is_valid_password(password):
        return False, "Password must be at least 6 characters."

    if role not in ("Administrator", "Librarian"):
        return False, "Role must be Administrator or Librarian."

    # Check if username already exists
    existing = execute_query(
        "SELECT UserID FROM users WHERE Username = %s",
        (username,),
        fetchone=True
    )
    if existing:
        return False, "Username already exists."

    try:
        password_hash = hash_password(password)
        user_id = execute_query(
            "INSERT INTO users (Username, PasswordHash, Role) VALUES (%s, %s, %s)",
            (username, password_hash, role),
            commit=True
        )
        if current_user_id:
            log_action(current_user_id, f"User created: {username} ({role})")
        return True, user_id
    except Exception as e:
        return False, str(e)


def change_user_password(user_id: int, new_password: str, current_user_id=None):
    if not is_valid_password(new_password):
        return False, "Password must be at least 6 characters."

    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found."

    try:
        new_hash = hash_password(new_password)
        execute_query(
            "UPDATE users SET PasswordHash = %s WHERE UserID = %s",
            (new_hash, user_id),
            commit=True
        )
        if current_user_id:
            log_action(current_user_id, f"Password changed for user: {user['Username']}")
        return True, "Password changed successfully."
    except Exception as e:
        return False, str(e)


def delete_user(user_id: int, current_user_id=None):
    user = get_user_by_id(user_id)
    if not user:
        return False, "User not found."

    # Prevent deleting yourself
    if current_user_id and user_id == current_user_id:
        return False, "You cannot delete your own account."

    # Prevent deleting the last Administrator
    if user["Role"] == "Administrator":
        admin_count = execute_query(
            "SELECT COUNT(*) as cnt FROM users WHERE Role = 'Administrator'",
            fetchone=True
        )
        if admin_count and admin_count["cnt"] <= 1:
            return False, "Cannot delete the last Administrator account."

    try:
        execute_query("DELETE FROM users WHERE UserID = %s", (user_id,), commit=True)
        if current_user_id:
            log_action(current_user_id, f"User deleted: {user['Username']}")
        return True, "User deleted successfully."
    except Exception as e:
        return False, str(e)


def change_own_password(user_id: int, old_password: str, new_password: str):
    """Allow a user to change their own password after verifying old one."""
    if not is_valid_password(new_password):
        return False, "New password must be at least 6 characters."

    try:
        row = execute_query(
            "SELECT PasswordHash, Username FROM users WHERE UserID = %s",
            (user_id,),
            fetchone=True
        )
        if not row:
            return False, "User not found."

        if not verify_password(old_password, row["PasswordHash"]):
            return False, "Current password is incorrect."

        new_hash = hash_password(new_password)
        execute_query(
            "UPDATE users SET PasswordHash = %s WHERE UserID = %s",
            (new_hash, user_id),
            commit=True
        )
        log_action(user_id, f"User '{row['Username']}' changed their own password")
        return True, "Password changed successfully."
    except Exception as e:
        return False, str(e)


def count_librarians():
    """Return number of Librarian accounts."""
    try:
        row = execute_query(
            "SELECT COUNT(*) as cnt FROM users WHERE Role = 'Librarian'",
            fetchone=True
        )
        return row["cnt"] if row else 0
    except Exception:
        return 0


def count_administrators():
    try:
        row = execute_query(
            "SELECT COUNT(*) as cnt FROM users WHERE Role = 'Administrator'",
            fetchone=True
        )
        return row["cnt"] if row else 0
    except Exception:
        return 0
