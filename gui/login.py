"""
Login Window - Library Management System
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Make sure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import login, create_default_admin
from config import APP_NAME, APPEARANCE_MODE, COLOR_THEME


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(f"{APP_NAME} - Login")
        self.geometry("420x380")
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        width = 420
        height = 380
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.current_user = None  # will hold logged-in user info

        self._build_ui()

        # Create default admin on first run
        create_default_admin()

    def _build_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(25, 5))

        subtitle = ctk.CTkLabel(
            main_frame,
            text="Please login to continue",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))

        # Username
        ctk.CTkLabel(main_frame, text="Username", anchor="w").pack(padx=40, fill="x")
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter username",
            height=38
        )
        self.username_entry.pack(padx=40, pady=(5, 15), fill="x")

        # Password
        ctk.CTkLabel(main_frame, text="Password", anchor="w").pack(padx=40, fill="x")
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter password",
            show="•",
            height=38
        )
        self.password_entry.pack(padx=40, pady=(5, 25), fill="x")

        # Login button
        login_btn = ctk.CTkButton(
            main_frame,
            text="Login",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_login
        )
        login_btn.pack(padx=40, pady=(0, 10), fill="x")

        # Exit button
        exit_btn = ctk.CTkButton(
            main_frame,
            text="Exit",
            height=36,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.destroy
        )
        exit_btn.pack(padx=40, pady=(0, 20), fill="x")

        # Bind Enter key
        self.bind("<Return>", lambda event: self._on_login())
        self.username_entry.focus()

    def _on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        try:
            user = login(username, password)
        except Exception as e:
            messagebox.showerror(
                "Server Offline",
                "Cannot connect to MySQL server.\n\n"
                "Please start MySQL and try again.\n\n"
                f"Details: {e}"
            )
            return

        if user:
            self.current_user = user
            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {user['Username']}!\nRole: {user['Role']}"
            )
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, "end")


def open_login():
    """Helper to open the login window and return the logged-in user."""
    app = LoginWindow()
    app.mainloop()
    return app.current_user
