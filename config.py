"""
Configuration settings for Library Management System
"""

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# MYSQL DATABASE SETTINGS
# ============================================================
# Write your MySQL password below
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "Root!^06@90$"          # <--- WRITE YOUR MYSQL PASSWORD HERE
DB_NAME = "library_management"

# Logs and backups
LOGS_DIR = os.path.join(BASE_DIR, "logs")
AUDIT_LOG_PATH = os.path.join(LOGS_DIR, "audit.log")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
LOGO_DISPLAY_PATH = os.path.join(ASSETS_DIR, "logo_display.png")
ICON_PATH = os.path.join(ASSETS_DIR, "icons", "app_icon.ico")
ICON_PNG_PATH = os.path.join(ASSETS_DIR, "icons", "icon_64.png")

# Application settings
APP_NAME = "Library Management System"
APP_VERSION = "1.0.0"

# Fine settings (default daily fine rate in ₹)
DEFAULT_FINE_RATE = 2.0  # ₹2 per day

# Loan period (days) — 1 month
DEFAULT_LOAN_DAYS = 30

# Maximum books a student can have issued at the same time
MAX_BOOKS_PER_STUDENT = 6

# Default admin credentials (will be hashed on first run)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_ROLE = "Administrator"

# UI Theme
APPEARANCE_MODE = "System"  # "System", "Dark", "Light"
COLOR_THEME = "blue"        # "blue", "green", "dark-blue"
