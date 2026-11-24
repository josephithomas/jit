"""Interactive drag-and-drop bucket tile with high aesthetic card styling."""
import os
from typing import List, Optional
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl


class DropZoneTile(QFrame):
    """Visual drop target tile that sorts dropped files directly into its designated folder."""

    files_dropped = pyqtSignal(list, str)  # (file_paths, target_directory)
    zone_edited = pyqtSignal(str)          # zone_id

    def __init__(
        self,
        zone_id: str,
        title: str,
        target_dir: str,
        icon: str = "📁",
        color_accent: str = "#6366f1",
        parent=None
    ):
        super().__init__(parent)
        self.zone_id = zone_id
        self.title_text = title
        self.target_dir = os.path.abspath(target_dir) if target_dir else ""
        self.icon_symbol = icon
        self.color_accent = color_accent
        self.item_count = 0

        self.setAcceptDrops(True)
        self.setMinimumSize(240, 160)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._init_ui()
        self._update_style(is_hover=False)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Top Bar: Icon container + Settings button
        top_layout = QHBoxLayout()
        
        # Icon badge with subtle background
        self.icon_badge = QLabel(self.icon_symbol)
        self.icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_badge.setFixedSize(42, 42)
        self.icon_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #1a2233;
                border: 1px solid {self.color_accent};
                border-radius: 10px;
                font-size: 22px;
            }}
        """)
        top_layout.addWidget(self.icon_badge)

        top_layout.addStretch()

        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setFixedSize(28, 28)
        self.btn_menu.setStyleSheet("""
            QPushButton {
                background-color: #161b26;
                border: 1px solid #283248;
                color: #94a3b8;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #242c40;
                color: #ffffff;
                border-color: #6366f1;
            }
        """)
        self.btn_menu.clicked.connect(self._show_menu)
        top_layout.addWidget(self.btn_menu)
        layout.addLayout(top_layout)

        # Title
        self.lbl_title = QLabel(self.title_text)
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(self.lbl_title)

        # Target Directory
        disp_dir = os.path.basename(self.target_dir) or self.target_dir or "Click to set folder"
        self.lbl_path = QLabel(f"📂 {disp_dir}")
        self.lbl_path.setToolTip(self.target_dir)
        self.lbl_path.setStyleSheet("font-size: 11px; color: #94a3b8;")
        self.lbl_path.setWordWrap(True)
        layout.addWidget(self.lbl_path)

        layout.addStretch()

        # Bottom Bar: Drop prompt & count badge
        bottom_layout = QHBoxLayout()
        self.lbl_prompt = QLabel("Drop files here")
        self.lbl_prompt.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")
        bottom_layout.addWidget(self.lbl_prompt)

        bottom_layout.addStretch()

        self.lbl_count = QLabel(f"{self.item_count} sorted")
        self.lbl_count.setStyleSheet(f"""
            QLabel {{
                background-color: #172033;
                color: #93c5fd;
                border: 1px solid #2b3954;
                padding: 3px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 700;
            }}
        """)
        bottom_layout.addWidget(self.lbl_count)
        layout.addLayout(bottom_layout)

    def _update_style(self, is_hover: bool = False):
        if is_hover:
            border_color = self.color_accent
            bg_color = "#151b28"
            border_style = "2px dashed"
        else:
            border_color = "#232c3f"
            bg_color = "#111520"
            border_style = "1px solid"

        self.setStyleSheet(f"""
            DropZoneTile {{
                background-color: {bg_color};
                border: {border_style} {border_color};
                border-radius: 12px;
            }}
        """)

    def _show_menu(self):
        menu = QMenu(self)
        action_change_path = menu.addAction("📁 Change Destination Folder...")
        action_choose_files = menu.addAction("📥 Add Files Manually...")
        action_open_folder = menu.addAction("↗ Open Folder in Explorer")

        act = menu.exec(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomRight()))
        if act == action_change_path:
            self._browse_target_folder()
        elif act == action_choose_files:
            self._browse_files_to_sort()
        elif act == action_open_folder:
            if os.path.exists(self.target_dir):
                os.startfile(self.target_dir)

    def _browse_target_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder", self.target_dir)
        if folder:
            self.target_dir = os.path.abspath(folder)
            disp = os.path.basename(self.target_dir) or self.target_dir
            self.lbl_path.setText(f"📂 {disp}")
            self.lbl_path.setToolTip(self.target_dir)
            self.zone_edited.emit(self.zone_id)

    def _browse_files_to_sort(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Sort into this Zone")
        if files:
            self.files_dropped.emit(files, self.target_dir)

    def increment_count(self, count: int = 1):
        self.item_count += count
        self.lbl_count.setText(f"{self.item_count} sorted")

    # Drag & Drop Events
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._update_style(is_hover=True)
            self.lbl_prompt.setText("Release to sort!")
            self.lbl_prompt.setStyleSheet("font-size: 11px; color: #34d399; font-weight: bold;")
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._update_style(is_hover=False)
        self.lbl_prompt.setText("Drop files here")
        self.lbl_prompt.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")

    def dropEvent(self, event):
        self.dragLeaveEvent(event)

        if not self.target_dir:
            self._browse_target_folder()
            if not self.target_dir:
                return

        urls = event.mimeData().urls()
        file_paths = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                file_paths.append(path)
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        file_paths.append(os.path.join(root, f))

        if file_paths:
            self.files_dropped.emit(file_paths, self.target_dir)
            event.acceptProposedAction()
