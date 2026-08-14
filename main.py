"""
Library Management System - Main Entry Point
"""

import os
import sys

# Ensure project root is always on the path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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
        print("Open config.py and set DB_PASSWORD, then run again.")
        # Still allow UI to open so user can see the app
        print("Opening application in OFFLINE mode...\n")
        server_online = False
    else:
        print("\nChecking MySQL server...")
        server_online = test_connection()
        if server_online:
            print("Server: ONLINE")
        else:
            print("Server: OFFLINE")
            print("Application will open, but database features will be disabled.")
            print("Start MySQL and use 'Refresh Status' on the dashboard.\n")

    print("Opening Login window...\n")
    user = open_login()

    if user:
        print(f"Logged in as: {user['Username']} ({user['Role']})")
        # Re-check status after login
        server_online = test_connection()
        app = DashboardWindow(user, server_online=server_online)
        app.mainloop()
    else:
        print("Login window closed.")


if __name__ == "__main__":
    main()
