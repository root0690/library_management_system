"""Shared window helpers (icon/logo)."""

import os
from config import ICON_PATH, ICON_PNG_PATH


def set_window_icon(window):
    """Apply the app crystal-book icon to any window."""
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
            window._icon_photo = photo  # keep reference alive
    except Exception:
        pass
