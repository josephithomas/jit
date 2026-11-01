"""Centralized asset and icon manager for Titus OmniSort Pro."""
import os
import sys
import base64
import ctypes
from typing import Optional
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QByteArray


def set_windows_app_id(app_id: str = "titus.omnisort.pro.2.0"):
    """Bakes the AppUserModelID into Windows Shell32 so taskbar uses app_icon.ico."""
    if sys.platform == 'win32':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass


def get_icon_path() -> str:
    """Finds absolute path to app_icon.ico across all deployment scenarios."""
    candidates = [
        # 1. Bundled PyInstaller temp directory
        os.path.join(getattr(sys, '_MEIPASS', ''), 'app_icon.ico'),
        # 2. Workspace root
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app_icon.ico'),
        # 3. Current working directory
        os.path.join(os.getcwd(), 'app_icon.ico'),
        # 4. Same directory as sys.argv[0]
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'app_icon.ico')
    ]
    for p in candidates:
        if p and os.path.isfile(p):
            return os.path.abspath(p)
    return ""


def get_app_icon() -> QIcon:
    """Returns a high-resolution QIcon loaded from app_icon.ico with multi-size fallback."""
    icon_path = get_icon_path()
    if icon_path and os.path.exists(icon_path):
        icon = QIcon(icon_path)
        if not icon.isNull():
            return icon

    # Fallback to app_icon.png if ico not found
    png_candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app_icon.png'),
        os.path.join(os.getcwd(), 'app_icon.png')
    ]
    for p in png_candidates:
        if p and os.path.isfile(p):
            icon = QIcon(p)
            if not icon.isNull():
                return icon

    return QIcon()


def get_app_pixmap(size: int = 36) -> QPixmap:
    """Returns a crisp, scaled QPixmap of app_icon.ico for in-app UI branding."""
    icon = get_app_icon()
    if not icon.isNull():
        pix = icon.pixmap(size, size)
        if not pix.isNull():
            return pix
    # Empty fallback
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    return pix

