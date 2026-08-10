"""
Password hashing utilities using hashlib (SHA-256 + salt).
"""

import hashlib
import os


def hash_password(password: str, salt: bytes = None) -> str:
    """
    Hash a password with a random salt.
    Returns a string in the format: salt_hex:hash_hex
    """
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000  # iterations
    )
    return f"{salt.hex()}:{pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored salt:hash string.
    """
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        new_hash = hash_password(password, salt)
        return new_hash == stored_hash
    except (ValueError, AttributeError):
        return False
