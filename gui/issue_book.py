"""
Issue Book Window
"""

import customtkinter as ctk
from tkinter import messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.window_utils import set_window_icon
from services.transaction_service import issue_book
from utils.date_utils import today_str, calculate_due_date
from config import DEFAULT_LOAN_DAYS, MAX_BOOKS_PER_STUDENT


class IssueBookWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user, server_online: bool = True):
        super().__init__(parent)
        set_window_icon(self)
        self.current_user = current_user
        self.server_online = server_online
        self.title("Issue Book")
        self.geometry("440x460")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _offline_guard(self):
        if not self.server_online:
            messagebox.showwarning(
                "Server Offline",
                "MySQL server is not running.\n\nStart the server and try again.",
                parent=self,
            )
            return True
        return False

    def _build_ui(self):
        if not self.server_online:
            banner = ctk.CTkFrame(self, height=34, fg_color="#8B0000", corner_radius=0)
            banner.pack(fill="x")
            ctk.CTkLabel(
                banner,
                text="SERVER NOT RUNNING — Issuing is disabled until MySQL is online.",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
            ).pack(pady=6)

        frame = ctk.CTkFrame(self)
        frame.pack(padx=25, pady=25, fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="Issue Book to Student",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 15))

        ctk.CTkLabel(frame, text="Student ID *").pack(anchor="w", padx=30)
        self.student_entry = ctk.CTkEntry(frame, height=36, placeholder_text="Enter Student ID")
        self.student_entry.pack(fill="x", padx=30, pady=(5, 12))

        ctk.CTkLabel(frame, text="Book ID *").pack(anchor="w", padx=30)
        self.book_entry = ctk.CTkEntry(frame, height=36, placeholder_text="Enter Book ID")
        self.book_entry.pack(fill="x", padx=30, pady=(5, 12))

        issue_date = today_str()
        due_date = calculate_due_date(issue_date, DEFAULT_LOAN_DAYS)

        ctk.CTkLabel(frame, text=f"Issue Date: {issue_date}", text_color="gray").pack(anchor="w", padx=30)
        ctk.CTkLabel(
            frame,
            text=f"Due Date: {due_date}  (Loan period: 1 month / {DEFAULT_LOAN_DAYS} days)",
            text_color="gray"
        ).pack(anchor="w", padx=30, pady=(0, 6))
        ctk.CTkLabel(
            frame,
            text=f"Limit: max {MAX_BOOKS_PER_STUDENT} books per student at a time",
            text_color="gray"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        ctk.CTkButton(
            frame, text="Issue Book", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._issue
        ).pack(fill="x", padx=30, pady=5)

        ctk.CTkButton(
            frame, text="Close", height=35, fg_color="transparent",
            border_width=1, command=self.destroy
        ).pack(fill="x", padx=30, pady=(5, 15))

    def _issue(self):
        if self._offline_guard():
            return
        sid = self.student_entry.get().strip()
        bid = self.book_entry.get().strip()

        if not sid or not bid:
            messagebox.showwarning("Input Error", "Please enter both Student ID and Book ID.", parent=self)
            return

        ok, msg = issue_book(sid, bid, user_id=self.current_user["UserID"])
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self.student_entry.delete(0, "end")
            self.book_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", msg, parent=self)
