"""
Books Management Window
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.book_service import get_all_books, add_book, update_book, delete_book, get_book_by_id


class BooksWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.title("Book Management")
        self.geometry("900x550")
        self.resizable(True, True)

        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        # Search bar
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(top, placeholder_text="Search by title, author, ISBN...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._refresh_table())

        ctk.CTkButton(top, text="Search", width=80, command=self._refresh_table).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh_table).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Add Book", width=100, command=self._add_book).pack(side="right", padx=5)

        # Table
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("ID", "ISBN", "Title", "Author", "Category", "Qty", "Available")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.column("Title", width=200, anchor="w")
        self.tree.column("Author", width=150, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="Edit Selected", command=self._edit_book).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="#c0392b", hover_color="#a93226",
                      command=self._delete_book).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy).pack(side="right", padx=5)

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search = self.search_entry.get()
        books = get_all_books(search if search else None)
        if books:
            for b in books:
                self.tree.insert("", "end", values=(
                    b["BookID"], b["ISBN"] or "", b["Title"], b["Author"],
                    b["Category"] or "", b["Quantity"], b["AvailableQuantity"]
                ))

    def _get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book first.", parent=self)
            return None
        return self.tree.item(selected[0])["values"][0]

    def _add_book(self):
        dialog = BookFormDialog(self, "Add New Book")
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = add_book(**dialog.result, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", f"Book added (ID: {msg})", parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _edit_book(self):
        book_id = self._get_selected_id()
        if not book_id:
            return
        book = get_book_by_id(book_id)
        if not book:
            return
        dialog = BookFormDialog(self, "Edit Book", book)
        self.wait_window(dialog)
        if dialog.result:
            ok, msg = update_book(book_id, **dialog.result, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _delete_book(self):
        book_id = self._get_selected_id()
        if not book_id:
            return
        if messagebox.askyesno("Confirm", "Delete this book?", parent=self):
            ok, msg = delete_book(book_id, user_id=self.current_user["UserID"])
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self._refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)


class BookFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, book=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x420")
        self.resizable(False, False)
        self.result = None
        self.book = book

        self.grab_set()
        self._build()

    def _build(self):
        fields = [
            ("ISBN", "isbn"),
            ("Title *", "title"),
            ("Author *", "author"),
            ("Category", "category"),
            ("Quantity *", "quantity"),
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(self, text=label).pack(padx=30, anchor="w", pady=(10 if i == 0 else 5, 0))
            entry = ctk.CTkEntry(self, height=35)
            entry.pack(padx=30, fill="x", pady=3)
            self.entries[key] = entry

        if self.book:
            self.entries["isbn"].insert(0, self.book.get("ISBN") or "")
            self.entries["title"].insert(0, self.book.get("Title") or "")
            self.entries["author"].insert(0, self.book.get("Author") or "")
            self.entries["category"].insert(0, self.book.get("Category") or "")
            self.entries["quantity"].insert(0, str(self.book.get("Quantity") or 1))
        else:
            self.entries["quantity"].insert(0, "1")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Save", width=100, command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left")

    def _save(self):
        self.result = {
            "isbn": self.entries["isbn"].get(),
            "title": self.entries["title"].get(),
            "author": self.entries["author"].get(),
            "category": self.entries["category"].get(),
            "quantity": self.entries["quantity"].get(),
        }
        self.destroy()
