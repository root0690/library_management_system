"""
Login Window - Library Management System
Supports online and offline login.
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import login, create_default_admin
from config import APP_NAME, APPEARANCE_MODE, COLOR_THEME, LOGO_DISPLAY_PATH, ICON_PATH, ICON_PNG_PATH


def set_window_icon(window):
    """Set application icon on a window (Windows + cross-platform)."""
    try:
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
    except Exception:
        pass
    try:
        if os.path.exists(ICON_PNG_PATH):
            from PIL import ImageTk
            img = Image.open(ICON_PNG_PATH)
            photo = ImageTk.PhotoImage(img)
            window.iconphoto(True, photo)
            window._icon_photo = photo
    except Exception:
        pass


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(f"{APP_NAME} - Login")
        self.geometry("420x500")
        self.resizable(False, False)
        set_window_icon(self)

        self.update_idletasks()
        width, height = 420, 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.current_user = None
        self._build_ui()

        try:
            create_default_admin()
        except Exception:
            pass

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=30, pady=25, fill="both", expand=True)

        if os.path.exists(LOGO_DISPLAY_PATH):
            try:
                logo_img = ctk.CTkImage(
                    light_image=Image.open(LOGO_DISPLAY_PATH),
                    dark_image=Image.open(LOGO_DISPLAY_PATH),
                    size=(100, 100),
                )
                ctk.CTkLabel(main_frame, image=logo_img, text="").pack(pady=(18, 8))
            except Exception:
                pass

        ctk.CTkLabel(
            main_frame, text=APP_NAME, font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            main_frame,
            text="Please login to continue",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            main_frame,
            text="Offline login works when MySQL is not running",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(pady=(0, 14))

        ctk.CTkLabel(main_frame, text="Username", anchor="w").pack(padx=40, fill="x")
        self.username_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Enter username", height=38
        )
        self.username_entry.pack(padx=40, pady=(5, 12), fill="x")

        ctk.CTkLabel(main_frame, text="Password", anchor="w").pack(padx=40, fill="x")
        self.password_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Enter password", show="•", height=38
        )
        self.password_entry.pack(padx=40, pady=(5, 20), fill="x")

        ctk.CTkButton(
            main_frame,
            text="Login",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_login,
        ).pack(padx=40, pady=(0, 8), fill="x")

        ctk.CTkButton(
            main_frame,
            text="Exit",
            height=36,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.destroy,
        ).pack(padx=40, pady=(0, 15), fill="x")

        self.bind("<Return>", lambda event: self._on_login())
        self.username_entry.focus()

    def _on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Input Error", "Please enter both username and password."
            )
            return

        user = login(username, password)

        if user:
            self.current_user = user
            offline = user.get("Offline", False)
            if offline:
                messagebox.showinfo(
                    "Login Successful (Offline Mode)",
                    f"Welcome, {user['Username']}!\n"
                    f"Role: {user['Role']}\n\n"
                    f"MySQL server is offline.\n"
                    f"You can use the dashboard, but database features are disabled.\n"
                    f"Start MySQL and click Refresh Status to go online.",
                )
            else:
                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {user['Username']}!\nRole: {user['Role']}",
                )
            self.destroy()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.\n\n"
                "If MySQL is offline, use:\n"
                "  Username: admin  (or root)\n"
                "  Password: admin123",
            )
            self.password_entry.delete(0, "end")


def open_login():
    app = LoginWindow()
    app.mainloop()
    return app.current_user
