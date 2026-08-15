"""
Return Book Window
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.transaction_service import get_active_issues, return_book, get_issue_by_id
from services.fine_service import calculate_fine, get_overdue_days
from utils.date_utils import today_str


class ReturnBookWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Return Book")
        self.geometry("800x500")
        self.grab_set()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="Search by title, student name, or Issue ID...", width=350
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._refresh())

        ctk.CTkButton(top, text="Search", width=80, command=self._refresh).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh).pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("IssueID", "Book", "Student", "Issue Date", "Due Date", "Overdue Days")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")
        self.tree.column("Book", width=180, anchor="w")
        self.tree.column("Student", width=140, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            btn_frame, text="Return Selected Book", height=38,
            font=ctk.CTkFont(weight="bold"),
            command=self._return
        ).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=5)

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            search = self.search_entry.get()
            issues = get_active_issues(search if search else None)
            if issues:
                for i in issues:
                    try:
                        overdue = get_overdue_days(i["DueDate"])
                    except Exception:
                        overdue = 0
                    self.tree.insert("", "end", values=(
                        i["IssueID"],
                        i.get("Title", ""),
                        i.get("StudentName", ""),
                        str(i.get("IssueDate", "")),
                        str(i.get("DueDate", "")),
                        overdue
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load issued books:\n{e}", parent=self)

    def _return(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction first.", parent=self)
            return

        try:
            issue_id = self.tree.item(selected[0])["values"][0]
            issue_id = int(issue_id)
        except Exception:
            messagebox.showerror("Error", "Invalid Issue ID selected.", parent=self)
            return

        try:
            issue = get_issue_by_id(issue_id)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load transaction:\n{e}", parent=self)
            return

        if not issue:
            messagebox.showerror("Error", "Transaction not found.", parent=self)
            return

        try:
            fine = calculate_fine(issue["DueDate"], today_str())
        except Exception:
            fine = 0.0

        confirm_msg = (
            f"Return book: {issue.get('Title', '')}\n"
            f"Student: {issue.get('StudentName', '')}\n"
            f"Estimated Fine: Rs.{fine:.2f}\n\n"
            f"Confirm return?"
        )
        if not messagebox.askyesno("Confirm Return", confirm_msg, parent=self):
            return

        try:
            ok, msg, fine_amount = return_book(issue_id, user_id=self.current_user["UserID"])
        except Exception as e:
            messagebox.showerror("Error", f"Return failed:\n{e}", parent=self)
            return

        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self._refresh()
        else:
            messagebox.showerror("Error", msg, parent=self)
