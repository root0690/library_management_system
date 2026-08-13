"""
User Management Window (Administrator only)
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_service import (
    get_all_users, add_user, change_user_password, delete_user, change_own_password
)


class UsersWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("User Management")
        self.geometry("750x520")
        self.grab_set()

        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        # Top buttons
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(top, text="System Users", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        ctk.CTkButton(top, text="Add New User", width=120, command=self._add_user).pack(side="right", padx=5)
        ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh_table).pack(side="right", padx=5)

        # Table
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "Username", "Role", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.column("Username", width=180, anchor="w")
        self.tree.column("Created At", width=180)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="Change Password", command=self._change_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete User", fg_color="#c0392b", hover_color="#a93226",
                      command=self._delete_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Change My Password", command=self._change_own_password).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=5)

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        users = get_all_users()
        for u in users:
            self.tree.insert("", "end", values=(
                u["UserID"], u["Username"], u["Role"], str(u["CreatedAt"])
            ))

    def _get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a user first.", parent=self)
            return None
        return int(self.tree.item(selected[0])["values"][0])

    def _add_user(self):
        dialog = AddUserDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = add_user(
                dialog.result["username"],
                dialog.result["password"],
                dialog.result["role"],
                current_user_id=self.current_user["UserID"]
            )
            if ok:
                messagebox.showinfo("Success", f"User created successfully (ID: {msg})", parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _change_password(self):
        user_id = self._get_selected_id()
        if not user_id:
            return
        dialog = ChangePasswordDialog(self, "Change User Password")
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = change_user_password(
                user_id,
                dialog.result,
                current_user_id=self.current_user["UserID"]
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _delete_user(self):
        user_id = self._get_selected_id()
        if not user_id:
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?", parent=self):
            return
        ok, msg = delete_user(user_id, current_user_id=self.current_user["UserID"])
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self._refresh_table()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _change_own_password(self):
        dialog = ChangeOwnPasswordDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = change_own_password(
                self.current_user["UserID"],
                dialog.result["old"],
                dialog.result["new"]
            )
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
            else:
                messagebox.showerror("Error", msg, parent=self)


class AddUserDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New User")
        self.geometry("380x360")
        self.resizable(False, False)
        self.result = None
        self.grab_set()

        ctk.CTkLabel(self, text="Username *").pack(padx=30, anchor="w", pady=(20, 0))
        self.username_entry = ctk.CTkEntry(self, height=35)
        self.username_entry.pack(padx=30, fill="x", pady=5)

        ctk.CTkLabel(self, text="Password *").pack(padx=30, anchor="w", pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self, height=35, show="•")
        self.password_entry.pack(padx=30, fill="x", pady=5)

        ctk.CTkLabel(self, text="Role *").pack(padx=30, anchor="w", pady=(10, 0))
        self.role_var = ctk.StringVar(value="Librarian")
        role_menu = ctk.CTkOptionMenu(self, variable=self.role_var,
                                      values=["Administrator", "Librarian"], height=35)
        role_menu.pack(padx=30, fill="x", pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=25)
        ctk.CTkButton(btn_frame, text="Create", width=100, command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left")

    def _save(self):
        self.result = {
            "username": self.username_entry.get(),
            "password": self.password_entry.get(),
            "role": self.role_var.get()
        }
        self.destroy()


class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Change Password"):
        super().__init__(parent)
        self.title(title)
        self.geometry("360x220")
        self.resizable(False, False)
        self.result = None
        self.grab_set()

        ctk.CTkLabel(self, text="New Password *").pack(padx=30, anchor="w", pady=(30, 0))
        self.password_entry = ctk.CTkEntry(self, height=35, show="•")
        self.password_entry.pack(padx=30, fill="x", pady=8)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Save", width=100, command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left")

    def _save(self):
        self.result = self.password_entry.get()
        self.destroy()


class ChangeOwnPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Change My Password")
        self.geometry("360x300")
        self.resizable(False, False)
        self.result = None
        self.grab_set()

        ctk.CTkLabel(self, text="Current Password *").pack(padx=30, anchor="w", pady=(25, 0))
        self.old_entry = ctk.CTkEntry(self, height=35, show="•")
        self.old_entry.pack(padx=30, fill="x", pady=5)

        ctk.CTkLabel(self, text="New Password *").pack(padx=30, anchor="w", pady=(15, 0))
        self.new_entry = ctk.CTkEntry(self, height=35, show="•")
        self.new_entry.pack(padx=30, fill="x", pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=25)
        ctk.CTkButton(btn_frame, text="Save", width=100, command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left")

    def _save(self):
        self.result = {
            "old": self.old_entry.get(),
            "new": self.new_entry.get()
        }
        self.destroy()
