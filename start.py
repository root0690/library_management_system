"""
Library Management System - Python Launcher
Use this file to start the whole system (instead of a .bat file).

Run:
    python start.py
"""

import sys
import os
import subprocess

def main():
    # Project root = folder where this start.py lives
    root = os.path.dirname(os.path.abspath(__file__))

    # Make sure Python can find our modules
    if root not in sys.path:
        sys.path.insert(0, root)

    # Change working directory to project root
    os.chdir(root)

    print("=" * 50)
    print("  Library Management System - Launcher")
    print("=" * 50)
    print(f"Project folder: {root}")
    print(f"Python: {sys.executable}")
    print()

    # Install / update requirements
    req_file = os.path.join(root, "requirements.txt")
    if os.path.exists(req_file):
        print("Checking required libraries...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
            print("Libraries OK.")
        except Exception as e:
            print(f"Warning: could not install requirements automatically ({e})")
            print("You can run manually: pip install -r requirements.txt")
    print()

    # Start the main application
    print("Starting application...")
    print("-" * 50)

    # Import and run main
    from main import main as app_main
    app_main()


if __name__ == "__main__":
    main()
