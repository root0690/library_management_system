"""
Reports Window
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.report_service import (
    inventory_report, overdue_report, transaction_report,
    student_activity_report, export_report_to_text
)


class ReportsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Reports")
        self.geometry("900x550")
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        left = ctk.CTkFrame(self, width=200)
        left.pack(side="left", fill="y", padx=10, pady=10)
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="Select Report", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

        reports = [
            ("Inventory Report", self._show_inventory),
            ("Overdue Report", self._show_overdue),
            ("Transaction Report", self._show_transactions),
            ("Student Activity", self._show_student_activity),
        ]
        for text, cmd in reports:
            ctk.CTkButton(left, text=text, command=cmd, height=40).pack(fill="x", padx=15, pady=6)

        ctk.CTkButton(left, text="Close", fg_color="gray", command=self.destroy).pack(side="bottom", pady=15, padx=15)

        # Right side - results
        self.right = ctk.CTkFrame(self)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.info_label = ctk.CTkLabel(self.right, text="Select a report from the left menu",
                                       font=ctk.CTkFont(size=14))
        self.info_label.pack(pady=30)

        self.tree_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _clear_tree(self):
        for w in self.tree_frame.winfo_children():
            w.destroy()
        self.info_label.pack_forget()

    def _show_inventory(self):
        self._clear_tree()
        data = inventory_report()
        stats = data["stats"]
        ctk.CTkLabel(
            self.tree_frame,
            text=f"Titles: {stats.get('total_titles', 0)}  |  Copies: {stats.get('total_copies', 0)}  |  "
                 f"Available: {stats.get('available_copies', 0)}  |  Issued: {stats.get('issued_copies', 0)}",
            font=ctk.CTkFont(size=13)
        ).pack(pady=5)

        columns = ("ID", "ISBN", "Title", "Author", "Category", "Qty", "Available")
        tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.column("Title", width=180)
        tree.pack(fill="both", expand=True)

        for b in data["books"]:
            tree.insert("", "end", values=(
                b["BookID"], b["ISBN"] or "", b["Title"], b["Author"],
                b["Category"] or "", b["Quantity"], b["AvailableQuantity"]
            ))

        def export():
            lines = [f"{b['BookID']}\t{b['Title']}\t{b['Author']}\t{b['Quantity']}\t{b['AvailableQuantity']}"
                     for b in data["books"]]
            path = export_report_to_text("Inventory", lines)
            messagebox.showinfo("Exported", f"Saved to:\n{path}", parent=self)

        ctk.CTkButton(self.tree_frame, text="Export to File", command=export).pack(pady=8)

    def _show_overdue(self):
        self._clear_tree()
        rows = overdue_report()
        ctk.CTkLabel(self.tree_frame, text=f"Overdue Books: {len(rows)}",
                     font=ctk.CTkFont(size=13)).pack(pady=5)

        columns = ("IssueID", "Title", "Student", "Issue Date", "Due Date", "Days Overdue")
        tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110)
        tree.column("Title", width=180)
        tree.pack(fill="both", expand=True)

        for r in rows:
            tree.insert("", "end", values=(
                r["IssueID"], r["Title"], r["StudentName"],
                str(r["IssueDate"]), str(r["DueDate"]), r["OverdueDays"]
            ))

    def _show_transactions(self):
        self._clear_tree()
        rows = transaction_report()
        columns = ("IssueID", "Title", "Student", "Issue Date", "Due Date", "Return Date", "Fine", "Status")
        tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=16)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=90)
        tree.column("Title", width=150)
        tree.pack(fill="both", expand=True)

        for r in rows:
            tree.insert("", "end", values=(
                r["IssueID"], r["Title"], r["StudentName"],
                str(r["IssueDate"]), str(r["DueDate"]),
                str(r["ReturnDate"] or ""), r["Fine"], r["Status"]
            ))

    def _show_student_activity(self):
        self._clear_tree()
        rows = student_activity_report()
        columns = ("StudentID", "Name", "Total Issues", "Currently Issued")
        tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=16)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        tree.pack(fill="both", expand=True)

        for r in rows:
            tree.insert("", "end", values=(
                r["StudentID"], r["Name"], r["TotalIssues"], r["CurrentlyIssued"]
            ))
