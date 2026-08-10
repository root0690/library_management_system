"""
Settings Window - Backup, Fine Rate, System Info
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import sys, os, shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    APP_NAME, APP_VERSION, DEFAULT_FINE_RATE, DEFAULT_LOAN_DAYS,
    BACKUPS_DIR, DB_HOST, DB_NAME, DB_USER
)
from services.auth_service import log_action
from database import execute_query


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Settings")
        self.geometry("480x520")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 20))

        # Fine rate
        ctk.CTkLabel(frame, text="Daily Fine Rate (₹)", anchor="w").pack(padx=30, fill="x")
        self.fine_entry = ctk.CTkEntry(frame, height=36)
        self.fine_entry.insert(0, str(DEFAULT_FINE_RATE))
        self.fine_entry.pack(padx=30, fill="x", pady=(5, 15))

        ctk.CTkLabel(frame, text="Note: Fine rate is currently read from config.py.\nChange the value in config.py and restart the app for permanent change.",
                     font=ctk.CTkFont(size=11), text_color="gray", justify="left").pack(padx=30, anchor="w")

        # Backup section
        ctk.CTkLabel(frame, text="Database Backup", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(25, 10))

        ctk.CTkButton(frame, text="Create Backup (SQL Dump)", height=40,
                      command=self._create_backup).pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(frame, text=f"Backups are saved in: {BACKUPS_DIR}",
                     font=ctk.CTkFont(size=11), text_color="gray").pack(padx=30, anchor="w", pady=5)

        # System info
        ctk.CTkLabel(frame, text="System Information", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(25, 10))

        info = (
            f"Application : {APP_NAME} v{APP_VERSION}\n"
            f"Database    : {DB_NAME} @ {DB_HOST}\n"
            f"User        : {self.current_user['Username']} ({self.current_user['Role']})\n"
            f"Loan Period : {DEFAULT_LOAN_DAYS} days\n"
            f"Fine Rate   : ₹{DEFAULT_FINE_RATE} per day"
        )
        ctk.CTkLabel(frame, text=info, justify="left", font=ctk.CTkFont(size=13)).pack(padx=30, anchor="w")

        ctk.CTkButton(frame, text="Close", height=36, fg_color="gray",
                      command=self.destroy).pack(pady=20, padx=30, fill="x")

    def _create_backup(self):
        try:
            os.makedirs(BACKUPS_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.sql"
            filepath = os.path.join(BACKUPS_DIR, filename)

            # Simple data dump
            tables = ["users", "books", "students", "issues", "auditlogs"]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"-- Library Management System Backup\n")
                f.write(f"-- Created: {datetime.now()}\n\n")
                f.write(f"USE {DB_NAME};\n\n")

                for table in tables:
                    rows = execute_query(f"SELECT * FROM {table}", fetchall=True)
                    f.write(f"-- Table: {table}\n")
                    if rows:
                        for row in rows:
                            cols = ", ".join(row.keys())
                            vals = []
                            for v in row.values():
                                if v is None:
                                    vals.append("NULL")
                                elif isinstance(v, (int, float)):
                                    vals.append(str(v))
                                else:
                                    vals.append("'" + str(v).replace("'", "''") + "'")
                            f.write(f"INSERT INTO {table} ({cols}) VALUES ({', '.join(vals)});\n")
                    f.write("\n")

            log_action(self.current_user["UserID"], f"Database backup created: {filename}")
            messagebox.showinfo("Backup Created", f"Backup saved to:\n{filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e), parent=self)
