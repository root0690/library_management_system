"""
Database connection module - MySQL version
"""

import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Global flag so the rest of the app knows if server is reachable
SERVER_ONLINE = False


def get_connection():
    """Create and return a new MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Cannot connect to MySQL server: {e}")


def test_connection():
    """
    Test if the MySQL connection works.
    Updates SERVER_ONLINE flag.
    Returns True if successful, False otherwise.
    """
    global SERVER_ONLINE
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            cursor.close()
            conn.close()
            SERVER_ONLINE = True
            print(f"Successfully connected to database: {db_name[0]}")
            return True
    except Exception as e:
        SERVER_ONLINE = False
        print(f"Connection failed: {e}")
        return False


def is_server_online():
    """Quick check / return last known status, and refresh it."""
    return test_connection()


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Helper to run a query safely.
    Raises ConnectionError if server is unreachable.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        if commit:
            conn.commit()
            if cursor.lastrowid:
                result = cursor.lastrowid

        cursor.close()
        return result

    except Error as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    except ConnectionError:
        raise
    finally:
        if conn and getattr(conn, "is_connected", lambda: False)():
            conn.close()
