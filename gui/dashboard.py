"""
Dashboard Window
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, APPEARANCE_MODE, COLOR_THEME
from services.book_service import get_book_stats
from services.student_service import get_student_stats
from services.transaction_service import get_transaction_stats
from services.auth_service import log_action


class DashboardWindow(ctk.CTk):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user

        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(f"{APP_NAME} - Dashboard")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Center
        self.update_idletasks()
        w, h = 1000, 650
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self._load_stats()

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, height=60, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top, text=APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=20, pady=15)

        user_label = ctk.CTkLabel(
            top,
            text=f"{self.current_user['Username']} ({self.current_user['Role']})",
            font=ctk.CTkFont(size=13)
        )
        user_label.pack(side="right", padx=20)

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Stats frame
        self.stats_frame = ctk.CTkFrame(content)
        self.stats_frame.pack(fill="x", pady=(0, 20))

        # Navigation buttons
        nav = ctk.CTkFrame(content)
        nav.pack(fill="both", expand=True)

        buttons = [
            ("📚  Books", self.open_books),
            ("👨‍🎓  Students", self.open_students),
            ("📤  Issue Book", self.open_issue),
            ("📥  Return Book", self.open_return),
            ("📊  Reports", self.open_reports),
            ("⚙️  Settings", self.open_settings),
        ]

        # Only Administrator can access Settings fully (we still show it)
        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(
                nav, text=text, height=70,
                font=ctk.CTkFont(size=16),
                command=cmd
            )
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15, sticky="nsew")

        for i in range(3):
            nav.grid_columnconfigure(i, weight=1)
        for i in range(2):
            nav.grid_rowconfigure(i, weight=1)

        # Logout
        logout_btn = ctk.CTkButton(
            self, text="Logout", width=120, height=35,
            fg_color="#c0392b", hover_color="#a93226",
            command=self._logout
        )
        logout_btn.pack(pady=10)

    def _load_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        try:
            bstats = get_book_stats()
            sstats = get_student_stats()
            tstats = get_transaction_stats()

            cards = [
                ("Total Books", bstats["total_copies"]),
                ("Available", bstats["available_copies"]),
                ("Issued", tstats["issued_books"]),
                ("Students", sstats["total_students"]),
                ("Overdue", tstats["overdue_books"]),
                ("Total Fines", f"₹{tstats['total_fines']:.2f}"),
            ]

            for i, (title, value) in enumerate(cards):
                card = ctk.CTkFrame(self.stats_frame, width=140, height=90)
                card.grid(row=0, column=i, padx=8, pady=10)
                card.pack_propagate(False)
                ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(15, 0))
                ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12)).pack()
        except Exception as e:
            ctk.CTkLabel(self.stats_frame, text=f"Could not load stats: {e}").pack(pady=20)

    def open_books(self):
        from gui.books import BooksWindow
        win = BooksWindow(self, self.current_user)
        win.grab_set()

    def open_students(self):
        from gui.students import StudentsWindow
        win = StudentsWindow(self, self.current_user)
        win.grab_set()

    def open_issue(self):
        from gui.issue_book import IssueBookWindow
        win = IssueBookWindow(self, self.current_user)
        win.grab_set()

    def open_return(self):
        from gui.return_book import ReturnBookWindow
        win = ReturnBookWindow(self, self.current_user)
        win.grab_set()

    def open_reports(self):
        from gui.reports import ReportsWindow
        win = ReportsWindow(self, self.current_user)
        win.grab_set()

    def open_settings(self):
        if self.current_user["Role"] != "Administrator":
            messagebox.showwarning("Access Denied", "Only Administrator can access Settings.")
            return
        from gui.settings import SettingsWindow
        win = SettingsWindow(self, self.current_user)
        win.grab_set()

    def _logout(self):
        log_action(self.current_user["UserID"], f"User '{self.current_user['Username']}' logged out")
        self.destroy()
        # Re-open login
        from gui.login import open_login
        user = open_login()
        if user:
            DashboardWindow(user).mainloop()
