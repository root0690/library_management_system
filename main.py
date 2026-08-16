"""
Library Management System - Main Entry Point
"""

import os
import sys

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
        print("Offline login is still available (admin / admin123).\n")
    else:
        print("\nChecking MySQL server...")
        if test_connection():
            print("Server: ONLINE")
        else:
            print("Server: OFFLINE — offline login is available.")

    print("Opening Login window...\n")
    user = open_login()

    if user:
        offline = user.get("Offline", False)
        # Prefer actual connection check; offline login forces offline dashboard
        server_online = False if offline else test_connection()
        mode = "OFFLINE" if not server_online else "ONLINE"
        print(f"Logged in as: {user['Username']} ({user['Role']}) — {mode}")
        app = DashboardWindow(user, server_online=server_online)
        app.mainloop()
    else:
        print("Login window closed.")


if __name__ == "__main__":
    main()
