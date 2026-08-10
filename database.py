"""
Database connection module - MySQL version
"""

import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    """
    Create and return a new MySQL connection.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise


def test_connection():
    """
    Test if the MySQL connection works.
    Returns True if successful, False otherwise.
    """
    try:
        conn = get_connection()
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            cursor.close()
            conn.close()
            print(f"Successfully connected to database: {db_name[0]}")
            return True
    except Error as e:
        print(f"Connection failed: {e}")
        return False


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Helper to run a query safely.
    - fetchone=True  → returns one row
    - fetchall=True  → returns list of rows
    - commit=True    → commits changes (INSERT/UPDATE/DELETE)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  # returns results as dictionaries

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
            # For INSERT, return last inserted id
            if cursor.lastrowid:
                result = cursor.lastrowid

        cursor.close()
        return result

    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn and conn.is_connected():
            conn.close()
