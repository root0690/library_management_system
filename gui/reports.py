"""
Reports Window
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.window_utils import set_window_icon

from services.report_service import (
    inventory_report, overdue_report, transaction_report,
    student_activity_report, export_report_to_pdf
)


class ReportsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user, server_online: bool = True):
        super().__init__(parent)

        set_window_icon(self)
        self.current_user = current_user
        self.server_online = server_online
        self.title("Reports")
        self.geometry("900x550")
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
                text="SERVER NOT RUNNING — Reports cannot be generated until MySQL is online.",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
            ).pack(pady=6)

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

        self.info_label = ctk.CTkLabel(
            self.right,
            text="Select a report from the left menu",
            font=ctk.CTkFont(size=14)
        )
        self.info_label.pack(pady=30)

        self.tree_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def _clear_tree(self):
        for w in self.tree_frame.winfo_children():
            w.destroy()
        self.info_label.pack_forget()

    def _show_offline_message(self):
        self._clear_tree()
        ctk.CTkLabel(
            self.tree_frame,
            text="Server not running — MySQL is offline.\nReport data cannot be loaded.",
            font=ctk.CTkFont(size=14),
            text_color="#922b21",
            justify="center",
        ).pack(pady=40)

    def _show_inventory(self):
        if not self.server_online:
            self._show_offline_message()
            return
        self._clear_tree()
        try:
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
                headers = ["ID", "ISBN", "Title", "Author", "Category", "Qty", "Available"]
                rows = [
                    [
                        b["BookID"], b["ISBN"] or "", b["Title"], b["Author"],
                        b["Category"] or "", b["Quantity"], b["AvailableQuantity"]
                    ]
                    for b in data["books"]
                ]
                subtitle = (
                    f"Titles: {stats.get('total_titles', 0)}  |  "
                    f"Copies: {stats.get('total_copies', 0)}  |  "
                    f"Available: {stats.get('available_copies', 0)}  |  "
                    f"Issued: {stats.get('issued_copies', 0)}"
                )
                try:
                    path = export_report_to_pdf("Inventory_Report", headers, rows, subtitle=subtitle)
                    messagebox.showinfo("Exported", f"PDF saved to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

            ctk.CTkButton(self.tree_frame, text="Export to PDF", command=export).pack(pady=8)
        except Exception as e:
            ctk.CTkLabel(
                self.tree_frame,
                text=f"Error loading report:\n{e}",
                text_color="#922b21",
            ).pack(pady=40)

    def _show_overdue(self):
        if not self.server_online:
            self._show_offline_message()
            return
        self._clear_tree()
        try:
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

            def export():
                headers = ["Issue ID", "Title", "Student", "Issue Date", "Due Date", "Days Overdue"]
                data_rows = [
                    [
                        r["IssueID"], r["Title"], r["StudentName"],
                        str(r["IssueDate"]), str(r["DueDate"]), r["OverdueDays"]
                    ]
                    for r in rows
                ]
                try:
                    path = export_report_to_pdf(
                        "Overdue_Report",
                        headers,
                        data_rows,
                        subtitle=f"Total overdue books: {len(rows)}"
                    )
                    messagebox.showinfo("Exported", f"PDF saved to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

            ctk.CTkButton(self.tree_frame, text="Export to PDF", command=export).pack(pady=8)
        except Exception as e:
            ctk.CTkLabel(
                self.tree_frame,
                text=f"Error loading report:\n{e}",
                text_color="#922b21",
            ).pack(pady=40)

    def _show_transactions(self):
        if not self.server_online:
            self._show_offline_message()
            return
        self._clear_tree()
        try:
            rows = transaction_report()
            ctk.CTkLabel(self.tree_frame, text=f"Recent Transactions: {len(rows)}",
                         font=ctk.CTkFont(size=13)).pack(pady=5)

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

            def export():
                headers = [
                    "Issue ID", "Title", "Student", "Issue Date",
                    "Due Date", "Return Date", "Fine", "Status"
                ]
                data_rows = [
                    [
                        r["IssueID"], r["Title"], r["StudentName"],
                        str(r["IssueDate"]), str(r["DueDate"]),
                        str(r["ReturnDate"] or ""), r["Fine"], r["Status"]
                    ]
                    for r in rows
                ]
                try:
                    path = export_report_to_pdf(
                        "Transaction_Report",
                        headers,
                        data_rows,
                        subtitle=f"Showing latest {len(rows)} transactions",
                        landscape_mode=True,
                    )
                    messagebox.showinfo("Exported", f"PDF saved to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

            ctk.CTkButton(self.tree_frame, text="Export to PDF", command=export).pack(pady=8)
        except Exception as e:
            ctk.CTkLabel(
                self.tree_frame,
                text=f"Error loading report:\n{e}",
                text_color="#922b21",
            ).pack(pady=40)

    def _show_student_activity(self):
        if not self.server_online:
            self._show_offline_message()
            return
        self._clear_tree()
        try:
            rows = student_activity_report()
            ctk.CTkLabel(self.tree_frame, text=f"Students: {len(rows)}",
                         font=ctk.CTkFont(size=13)).pack(pady=5)

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

            def export():
                headers = ["Student ID", "Name", "Total Issues", "Currently Issued"]
                data_rows = [
                    [r["StudentID"], r["Name"], r["TotalIssues"], r["CurrentlyIssued"]]
                    for r in rows
                ]
                try:
                    path = export_report_to_pdf(
                        "Student_Activity_Report",
                        headers,
                        data_rows,
                        subtitle=f"Total students: {len(rows)}"
                    )
                    messagebox.showinfo("Exported", f"PDF saved to:\n{path}", parent=self)
                except Exception as e:
                    messagebox.showerror("Export Failed", str(e), parent=self)

            ctk.CTkButton(self.tree_frame, text="Export to PDF", command=export).pack(pady=8)
        except Exception as e:
            ctk.CTkLabel(
                self.tree_frame,
                text=f"Error loading report:\n{e}",
                text_color="#922b21",
            ).pack(pady=40)
