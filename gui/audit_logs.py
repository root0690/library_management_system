"""
Audit Logs Window (Administrator only) - READ ONLY
Logs are immutable: cannot edit or delete from the app or database.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audit_service import get_audit_logs, get_audit_log_count


class AuditLogsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Audit Logs (Read Only)")
        self.geometry("900x560")
        self.grab_set()

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            top, text="System Audit Logs",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(top, text="", text_color="gray")
        self.count_label.pack(side="left", padx=15)

        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="Search action or username...", width=220
        )
        self.search_entry.pack(side="right", padx=(5, 0))
        self.search_entry.bind("<Return>", lambda e: self._refresh())

        ctk.CTkButton(top, text="Search", width=80, command=self._refresh).pack(side="right", padx=5)
        ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh).pack(side="right", padx=5)

        # Immutable notice
        notice = ctk.CTkLabel(
            self,
            text="These logs are immutable. They cannot be edited or deleted by users or the application.",
            font=ctk.CTkFont(size=12),
            text_color="#b03a2e"
        )
        notice.pack(pady=(0, 6))

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("LogID", "UserID", "Username", "Action", "Timestamp")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        self.tree.heading("LogID", text="Log ID")
        self.tree.heading("UserID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Action", text="Action")
        self.tree.heading("Timestamp", text="Timestamp")

        self.tree.column("LogID", width=70, anchor="center")
        self.tree.column("UserID", width=70, anchor="center")
        self.tree.column("Username", width=120, anchor="w")
        self.tree.column("Action", width=420, anchor="w")
        self.tree.column("Timestamp", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            bottom,
            text="Showing latest 500 entries. Use search to filter.",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        ).pack(side="left")

        ctk.CTkButton(bottom, text="Close", command=self.destroy).pack(side="right")

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_entry.get()
        logs = get_audit_logs(limit=500, search=search if search else None)
        total = get_audit_log_count()
        self.count_label.configure(text=f"(Total in database: {total})")

        for log in logs:
            self.tree.insert("", "end", values=(
                log.get("LogID", ""),
                log.get("UserID", "") if log.get("UserID") is not None else "",
                log.get("Username") or "(unknown)",
                log.get("Action", ""),
                str(log.get("Timestamp", ""))
            ))
