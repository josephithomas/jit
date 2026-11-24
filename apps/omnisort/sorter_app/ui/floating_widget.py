"""Floating desktop mini drop-target widget inspired by Abelssoft File Organizer."""
import os
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from .assets import get_app_icon, get_app_pixmap


class FloatingDropWidget(QWidget):
    """Semi-transparent, always-on-top floating desktop drop target."""

    files_dropped = pyqtSignal(list, str)  # (files, mode_or_target)
    open_main_window_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAcceptDrops(True)
        self.setFixedSize(260, 160)
        self.setWindowIcon(get_app_icon())
        self._drag_pos = QPoint()
        self._init_ui()

    def _init_ui(self):
        container = QFrame(self)
        container.setObjectName("floatingContainer")
        container.setGeometry(0, 0, 260, 160)
        container.setStyleSheet("""
            QFrame#floatingContainer {
                background-color: rgba(22, 25, 32, 0.94);
                border: 2px solid #6366f1;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 10)
        layout.setSpacing(6)

        # Header Bar: Title, Move Grip, Open & Close
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        ico_lbl = QLabel()
        ico_lbl.setPixmap(get_app_pixmap(18))
        header_layout.addWidget(ico_lbl)

        lbl_logo = QLabel("Titus OmniDrop")
        lbl_logo.setStyleSheet("font-size: 12px; font-weight: bold; color: #818cf8;")
        header_layout.addWidget(lbl_logo)

        header_layout.addStretch()

        btn_expand = QPushButton("⤢")
        btn_expand.setFixedSize(20, 20)
        btn_expand.setToolTip("Open Full Titus OmniSort Pro Window")
        btn_expand.setStyleSheet("background: transparent; color: #9ca3af; border: none; font-size: 13px;")
        btn_expand.clicked.connect(self.open_main_window_requested.emit)
        header_layout.addWidget(btn_expand)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.setToolTip("Hide Floating Widget")
        btn_close.setStyleSheet("background: transparent; color: #9ca3af; border: none; font-size: 11px;")
        btn_close.clicked.connect(self.hide)
        header_layout.addWidget(btn_close)

        layout.addLayout(header_layout)

        # Target preset combo
        self.combo_target = QComboBox()
        self.combo_target.addItems([
            "🌟 Auto-Sort by Category",
            "📄 Sort into Documents",
            "🖼️ Sort into Pictures",
            "⚡ Apply Custom Rules"
        ])
        self.combo_target.setStyleSheet("""
            QComboBox {
                background-color: #1a1d24;
                border: 1px solid #333846;
                border-radius: 4px;
                color: #e5e7eb;
                font-size: 11px;
                padding: 4px 6px;
            }
        """)
        layout.addWidget(self.combo_target)

        # Drop Area Frame
        self.drop_frame = QFrame()
        self.drop_frame.setStyleSheet("""
            QFrame {
                background-color: #16181e;
                border: 1px dashed #4b5563;
                border-radius: 8px;
            }
        """)
        drop_layout = QVBoxLayout(self.drop_frame)
        drop_layout.setContentsMargins(6, 6, 6, 6)

        self.lbl_drop_text = QLabel("Drag & Drop Files Here\nto sort instantly")
        self.lbl_drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_drop_text.setStyleSheet("font-size: 11px; color: #9ca3af;")
        drop_layout.addWidget(self.lbl_drop_text)

        layout.addWidget(self.drop_frame)

    # Window dragging with mouse
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # Drag & Drop handling
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_frame.setStyleSheet("""
                QFrame {
                    background-color: #1e2230;
                    border: 2px dashed #10b981;
                    border-radius: 8px;
                }
            """)
            self.lbl_drop_text.setText("Drop to Sort!")
            self.lbl_drop_text.setStyleSheet("font-size: 12px; color: #34d399; font-weight: bold;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_frame.setStyleSheet("""
            QFrame {
                background-color: #16181e;
                border: 1px dashed #4b5563;
                border-radius: 8px;
            }
        """)
        self.lbl_drop_text.setText("Drag & Drop Files Here\nto sort instantly")
        self.lbl_drop_text.setStyleSheet("font-size: 11px; color: #9ca3af;")

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        urls = event.mimeData().urls()
        files = []
        for u in urls:
            local = u.toLocalFile()
            if os.path.isfile(local):
                files.append(local)
            elif os.path.isdir(local):
                for root, _, fs in os.walk(local):
                    for f in fs:
                        files.append(os.path.join(root, f))

        if files:
            mode_text = self.combo_target.currentText()
            self.files_dropped.emit(files, mode_text)
            event.acceptProposedAction()

