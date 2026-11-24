"""Modern, high-aesthetic dark theme stylesheet for Titus OmniSort Pro."""

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0b0d13;
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QDialog {
    background-color: #0f121a;
    color: #f1f5f9;
}

/* MenuBar */
QMenuBar {
    background-color: #0d1017;
    color: #cbd5e1;
    border-bottom: 1px solid #1a202e;
    padding: 3px 6px;
    font-size: 12px;
    font-weight: 500;
}

QMenuBar::item {
    background: transparent;
    padding: 5px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1a2233;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #242f46;
}

/* Menus */
QMenu {
    background-color: #121622;
    color: #e2e8f0;
    border: 1px solid #283248;
    border-radius: 8px;
    padding: 5px;
    font-size: 12px;
}

QMenu::item {
    padding: 6px 28px 6px 12px;
    border-radius: 5px;
}

QMenu::item:selected {
    background-color: #242f46;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #232c3f;
    margin: 4px 6px;
}

/* ToolBar */
QToolBar {
    background-color: #10141d;
    border-bottom: 1px solid #1a202e;
    padding: 4px 8px;
    spacing: 6px;
}

QToolBar QToolButton {
    background-color: #171d2b;
    border: 1px solid #232c3f;
    border-radius: 6px;
    padding: 5px 12px;
    color: #cbd5e1;
    font-weight: 600;
    font-size: 12px;
}

QToolBar QToolButton:hover {
    background-color: #222b3e;
    border-color: #3d4b68;
    color: #ffffff;
}

QToolBar QToolButton:pressed {
    background-color: #131824;
}

QToolBar::separator {
    width: 1px;
    background-color: #232c3f;
    margin: 4px 6px;
}

/* StatusBar */
QStatusBar {
    background-color: #0a0c12;
    border-top: 1px solid #181d2a;
    color: #94a3b8;
    font-size: 11px;
    padding: 2px 6px;
}

QStatusBar::item {
    border: none;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #273042;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3b4760;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #273042;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3b4760;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Sidebar Navigation Buttons */
QPushButton.navBtn {
    text-align: left;
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    margin: 2px 8px;
}

QPushButton.navBtn:hover {
    background-color: #171c28;
    color: #f8fafc;
    border: 1px solid #232c3f;
}

QPushButton.navBtnActive {
    text-align: left;
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e2436, stop:1 #252e44);
    border: 1px solid #3b4766;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    margin: 2px 8px;
}

/* Standard Buttons */
QPushButton {
    background-color: #1b2130;
    color: #e2e8f0;
    border: 1px solid #2b354c;
    border-radius: 7px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #242c40;
    border-color: #435275;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #161b27;
}

QPushButton:disabled {
    background-color: #131722;
    color: #4b5563;
    border-color: #1f2536;
}

/* Gradient Primary Button */
QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #7c3aed);
    color: #ffffff;
    border: 1px solid #6366f1;
    font-size: 13px;
    font-weight: 700;
    padding: 10px 22px;
    border-radius: 8px;
}

QPushButton#btnPrimary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338ca, stop:1 #6d28d9);
    border-color: #818cf8;
}

QPushButton#btnPrimary:pressed {
    background: #3730a3;
}

/* Gradient Success Button */
QPushButton#btnSuccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: 1px solid #34d399;
    font-size: 13px;
    font-weight: 700;
    padding: 10px 24px;
    border-radius: 8px;
}

QPushButton#btnSuccess:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
    border-color: #6ee7b7;
}

QPushButton#btnSuccess:disabled {
    background: #142820;
    color: #4b6358;
    border-color: #1d382d;
}

/* Danger Button */
QPushButton#btnDanger {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #e11d48);
    color: #ffffff;
    border: 1px solid #f43f5e;
    font-size: 12px;
    font-weight: 700;
    padding: 8px 18px;
    border-radius: 7px;
}

QPushButton#btnDanger:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #991b1b, stop:1 #be123c);
}

/* Inputs & Combos */
QLineEdit, QComboBox, QSpinBox {
    background-color: #121622;
    border: 1px solid #283248;
    border-radius: 7px;
    padding: 8px 12px;
    color: #f1f5f9;
    font-size: 12px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #6366f1;
    background-color: #161c2c;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
    padding-right: 4px;
}

QComboBox QAbstractItemView {
    background-color: #141824;
    border: 1px solid #2b364e;
    border-radius: 6px;
    color: #f1f5f9;
    selection-background-color: #312e81;
    selection-color: #ffffff;
    padding: 6px;
    outline: none;
}

/* Tables & Trees */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #0f131c;
    border: 1px solid #1f2738;
    border-radius: 8px;
    gridline-color: #171d2b;
    color: #e2e8f0;
    selection-background-color: #1e2638;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item, QTreeWidget::item, QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #141924;
}

QTableWidget::item:hover, QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #171d2b;
}

QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #212a3e;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #131722;
    color: #94a3b8;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid #1d2435;
    border-bottom: 1px solid #1f273a;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #222b3d;
    border-radius: 6px;
    text-align: center;
    background-color: #10141d;
    color: #ffffff;
    font-weight: 700;
    font-size: 11px;
    height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:0.5 #8b5cf6, stop:1 #10b981);
    border-radius: 5px;
}

/* Checkboxes and Radios */
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #cbd5e1;
    font-size: 12px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #3b4764;
    border-radius: 4px;
    background-color: #141824;
}

QCheckBox::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

QRadioButton::indicator {
    width: 17px;
    height: 17px;
    border-radius: 9px;
    border: 1px solid #3b4764;
    background-color: #141824;
}

QRadioButton::indicator:hover {
    border-color: #6366f1;
}

QRadioButton::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}
"""
