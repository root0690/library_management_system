"""
Students Management Window
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.student_service import get_all_students, add_student, update_student, delete_student, get_student_by_id


class StudentsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Student Management")
        self.geometry("850x520")

        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(top, placeholder_text="Search by name, department, phone...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._refresh_table())

        ctk.CTkButton(top, text="Search", width=80, command=self._refresh_table).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh_table).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Add Student", width=110, command=self._add).pack(side="right", padx=5)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Name", "Department", "Semester", "Phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.column("Name", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(btn_frame, text="Edit Selected", command=self._edit).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="#c0392b", hover_color="#a93226",
                      command=self._delete).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=5)

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search = self.search_entry.get()
        students = get_all_students(search if search else None)
        if students:
            for s in students:
                self.tree.insert("", "end", values=(
                    s["StudentID"], s["Name"], s["Department"] or "",
                    s["Semester"] or "", s["Phone"] or ""
                ))

    def _get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a student first.", parent=self)
            return None
        return self.tree.item(selected[0])["values"][0]

    def _add(self):
        dialog = StudentFormDialog(self, "Add New Student")
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = add_student(**dialog.result, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", f"Student added (ID: {msg})", parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _edit(self):
        sid = self._get_selected_id()
        if not sid:
            return
        student = get_student_by_id(sid)
        if not student:
            return
        dialog = StudentFormDialog(self, "Edit Student", student)
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = update_student(sid, **dialog.result, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _delete(self):
        sid = self._get_selected_id()
        if not sid:
            return
        if messagebox.askyesno("Confirm", "Delete this student?", parent=self):
            ok, msg = delete_student(sid, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)


class StudentFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, student=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("380x380")
        self.resizable(False, False)
        self.result = None
        self.student = student
        self.grab_set()
        self._build()

    def _build(self):
        fields = [("Name *", "name"), ("Department", "department"),
                  ("Semester", "semester"), ("Phone", "phone")]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(self, text=label).pack(padx=30, anchor="w", pady=(12 if i == 0 else 5, 0))
            entry = ctk.CTkEntry(self, height=35)
            entry.pack(padx=30, fill="x", pady=3)
            self.entries[key] = entry

        if self.student:
            self.entries["name"].insert(0, self.student.get("Name") or "")
            self.entries["department"].insert(0, self.student.get("Department") or "")
            self.entries["semester"].insert(0, self.student.get("Semester") or "")
            self.entries["phone"].insert(0, self.student.get("Phone") or "")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Save", width=100, command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left")

    def _save(self):
        self.result = {
            "name": self.entries["name"].get(),
            "department": self.entries["department"].get(),
            "semester": self.entries["semester"].get(),
            "phone": self.entries["phone"].get(),
        }
        self.destroy()
