"""
Library Management System - Entry Point
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, DB_PASSWORD
from database import test_connection
from gui.login import open_login
from gui.dashboard import DashboardWindow


def main():
    print("=" * 50)
    print(f"  {APP_NAME} v{APP_VERSION}")
    print("=" * 50)

    if DB_PASSWORD == "":
        print("\nWARNING: MySQL password is empty in config.py")
        print("Please open config.py and write your password, then run again.")
        return

    print("\nTesting MySQL connection...")
    if not test_connection():
        print("Cannot connect to database. Please check config.py settings.")
        return

    print("Connection OK. Opening Login window...\n")

    user = open_login()

    if user:
        print(f"Logged in as: {user['Username']} ({user['Role']})")
        print("Opening Dashboard...")
        app = DashboardWindow(user)
        app.mainloop()
    else:
        print("Login cancelled or failed.")


if __name__ == "__main__":
    main()
