"""
Dashboard Window
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, APPEARANCE_MODE, COLOR_THEME, ICON_PATH, ICON_PNG_PATH
from services.book_service import get_book_stats
from services.student_service import get_student_stats
from services.transaction_service import get_transaction_stats
from services.auth_service import log_action
from services.user_service import count_librarians
from database import test_connection, SERVER_ONLINE
import os

def set_window_icon(window):
    try:
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
    except Exception:
        pass
    try:
        if os.path.exists(ICON_PNG_PATH):
            from PIL import Image, ImageTk
            img = Image.open(ICON_PNG_PATH)
            photo = ImageTk.PhotoImage(img)
            window.iconphoto(True, photo)
            window._icon_photo = photo
    except Exception:
        pass


class DashboardWindow(ctk.CTk):
    def __init__(self, current_user: dict, server_online: bool = True):
        super().__init__()
        self.current_user = current_user
        self.server_online = server_online

        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(f"{APP_NAME} - Dashboard")
        self.geometry("1050x680")
        self.minsize(900, 600)
        set_window_icon(self)

        self.update_idletasks()
        w, h = 1050, 680
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

        # Offline banner
        self.banner = ctk.CTkFrame(self, height=36, fg_color="#8B0000", corner_radius=0)
        self.banner_label = ctk.CTkLabel(
            self.banner,
            text="SERVER OFFLINE - Database functions are disabled. Start MySQL and click Refresh Status.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        self.banner_label.pack(pady=6)
        if not self.server_online:
            self.banner.pack(fill="x")

        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Stats frame
        self.stats_frame = ctk.CTkFrame(content)
        self.stats_frame.pack(fill="x", pady=(0, 15))

        # Navigation buttons
        nav = ctk.CTkFrame(content)
        nav.pack(fill="both", expand=True)

        buttons = [
            ("Books", self.open_books),
            ("Students", self.open_students),
            ("Issue Book", self.open_issue),
            ("Return Book", self.open_return),
            ("Reports", self.open_reports),
            ("Settings", self.open_settings),
        ]

        if self.current_user.get("Role") == "Administrator":
            buttons.append(("Users", self.open_users))
            buttons.append(("Refresh Status", self._refresh_status))

        for i, (text, cmd) in enumerate(buttons):
            btn = ctk.CTkButton(
                nav, text=text, height=70,
                font=ctk.CTkFont(size=15),
                command=cmd
            )
            btn.grid(row=i // 4, column=i % 4, padx=12, pady=12, sticky="nsew")

        for i in range(4):
            nav.grid_columnconfigure(i, weight=1)
        for i in range(3):
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

        # Always show server status card first
        status_text = "Online" if self.server_online else "Offline"
        status_color = "#1e8449" if self.server_online else "#922b21"

        cards = []

        # Server status
        cards.append(("Server", status_text, status_color))

        if self.server_online:
            try:
                bstats = get_book_stats()
                sstats = get_student_stats()
                tstats = get_transaction_stats()
                librarians = count_librarians()

                cards.extend([
                    ("Total Books", bstats["total_copies"], None),
                    ("Available", bstats["available_copies"], None),
                    ("Issued", tstats["issued_books"], None),
                    ("Students", sstats["total_students"], None),
                    ("Librarians", librarians, None),
                    ("Overdue", tstats["overdue_books"], None),
                    ("Total Fines", f"Rs.{tstats['total_fines']:.2f}", None),
                ])
            except Exception as e:
                cards.append(("Error", "DB Error", "#922b21"))
                print(f"Stats error: {e}")
        else:
            cards.extend([
                ("Total Books", "-", None),
                ("Available", "-", None),
                ("Issued", "-", None),
                ("Students", "-", None),
                ("Librarians", "-", None),
                ("Overdue", "-", None),
                ("Total Fines", "-", None),
            ])

        for i, item in enumerate(cards):
            title, value = item[0], item[1]
            color = item[2] if len(item) > 2 else None

            card = ctk.CTkFrame(self.stats_frame, width=115, height=90)
            card.grid(row=0, column=i, padx=6, pady=10)
            card.pack_propagate(False)

            val_label = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=18, weight="bold"))
            if color:
                val_label.configure(text_color=color)
            val_label.pack(pady=(15, 0))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11)).pack()

    def _require_server(self):
        if not self.server_online:
            messagebox.showwarning(
                "Server Offline",
                "MySQL server is not running.\n\nStart MySQL and click 'Refresh Status'.",
                parent=self
            )
            return False
        return True

    def _refresh_status(self):
        online = test_connection()
        self.server_online = online
        if online:
            self.banner.pack_forget()
            messagebox.showinfo("Server Status", "Server is Online.", parent=self)
        else:
            self.banner.pack(fill="x", after=self.winfo_children()[0] if self.winfo_children() else None)
            # Re-pack banner near top
            children = self.winfo_children()
            if self.banner not in children:
                self.banner.pack(fill="x")
            messagebox.showwarning("Server Status", "Server is still Offline.", parent=self)
        self._load_stats()

    def open_books(self):
        if not self._require_server():
            return
        from gui.books import BooksWindow
        win = BooksWindow(self, self.current_user)
        win.grab_set()

    def open_students(self):
        if not self._require_server():
            return
        from gui.students import StudentsWindow
        win = StudentsWindow(self, self.current_user)
        win.grab_set()

    def open_issue(self):
        if not self._require_server():
            return
        from gui.issue_book import IssueBookWindow
        win = IssueBookWindow(self, self.current_user)
        win.grab_set()

    def open_return(self):
        if not self._require_server():
            return
        from gui.return_book import ReturnBookWindow
        win = ReturnBookWindow(self, self.current_user)
        win.grab_set()

    def open_reports(self):
        if not self._require_server():
            return
        from gui.reports import ReportsWindow
        win = ReportsWindow(self, self.current_user)
        win.grab_set()

    def open_settings(self):
        if self.current_user["Role"] != "Administrator":
            messagebox.showwarning("Access Denied", "Only Administrator can access Settings.")
            return
        if not self._require_server():
            return
        from gui.settings import SettingsWindow
        win = SettingsWindow(self, self.current_user)
        win.grab_set()

    def open_users(self):
        if self.current_user["Role"] != "Administrator":
            messagebox.showwarning("Access Denied", "Only Administrator can manage users.")
            return
        if not self._require_server():
            return
        from gui.users import UsersWindow
        win = UsersWindow(self, self.current_user)
        win.grab_set()

    def _logout(self):
        if self.server_online:
            try:
                log_action(self.current_user["UserID"], f"User '{self.current_user['Username']}' logged out")
            except Exception:
                pass
        self.destroy()
        from gui.login import open_login
        user = open_login()
        if user:
            online = test_connection()
            DashboardWindow(user, server_online=online).mainloop()
