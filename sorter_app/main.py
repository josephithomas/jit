"""Titus OmniSort Pro main launcher entry point with baked app_icon.ico."""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ensure local imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sorter_app.ui.assets import set_windows_app_id, get_app_icon
from sorter_app.ui.main_window import MainWindow


def main():
    # 1. Bake app_icon into Windows taskbar AppUserModelID
    set_windows_app_id("titus.omnisort.pro.2.0")

    # 2. Enable high-DPI scaling
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Titus OmniSort Pro")
    app.setOrganizationName("Titus")

    # 3. Bake icon into global QApplication
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = MainWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
