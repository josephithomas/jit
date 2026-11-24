"""Master 2-in-1 File and Folder Sorter with a modern, high-aesthetic UI."""
import os
import sys
from typing import List, Optional, Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QCheckBox, 
    QRadioButton, QButtonGroup, QProgressBar, QMessageBox, 
    QScrollArea, QGridLayout, QFrame, QListWidget, QListWidgetItem,
    QSpinBox, QSplitter, QSystemTrayIcon, QMenu,
    QMenuBar, QToolBar, QStatusBar, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont, QAction, QKeySequence

from ..core.classifier import (
    get_file_category, get_date_brackets, get_size_bracket,
    format_file_size, CATEGORY_ICONS
)
from ..core.rule_engine import RuleEngine, Rule
from ..core.organizer_engine import OrganizerEngine, PlannedFileOperation
from ..core.undo_manager import UndoManager
from ..core.folder_watcher import FolderWatcher
from .theme import DARK_STYLESHEET
from .drop_zone_widget import DropZoneTile
from .floating_widget import FloatingDropWidget
from .rule_dialog import RuleDialog
from .duplicate_dialog import DuplicateCleanerWidget
from .history_dialog import HistoryUndoWidget
from .assets import get_app_icon, get_app_pixmap


class ExecutionWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished_exec = pyqtSignal(dict)

    def __init__(self, engine: OrganizerEngine, ops: List[PlannedFileOperation], desc: str, root: str, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.ops = ops
        self.desc = desc
        self.root = root

    def run(self):
        res = self.engine.execute_operations(
            operations=self.ops,
            batch_description=self.desc,
            source_root=self.root,
            progress_cb=lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
        )
        self.finished_exec.emit(res)


class MainWindow(QMainWindow):
    """The master 2-in-1 Titus OmniSort Pro window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Titus OmniSort Pro — 2-in-1 Folder & File Intelligent Sorter")
        self.setWindowIcon(get_app_icon())
        self.resize(1180, 780)
        self.setMinimumSize(980, 660)
        self.setStyleSheet(DARK_STYLESHEET)
        self.setAcceptDrops(True)

        # Core Engines
        app_data = os.path.join(os.path.expanduser("~"), ".omnisort_pro")
        os.makedirs(app_data, exist_ok=True)
        self.rule_engine = RuleEngine(config_file=os.path.join(app_data, "rules.json"))
        self.undo_manager = UndoManager(history_file=os.path.join(app_data, "sort_history.json"))
        self.engine = OrganizerEngine(self.rule_engine, self.undo_manager)
        self.watcher = FolderWatcher(self.engine, settle_seconds=3.0)
        self.watcher.event_callbacks.append(self._on_watcher_event)

        # State
        self.current_source_folder: str = ""
        self.planned_operations: List[PlannedFileOperation] = []
        self._exec_worker: Optional[ExecutionWorker] = None
        self.selected_preset: str = "category"

        # Floating Mini Widget
        self.floating_widget = FloatingDropWidget()
        self.floating_widget.files_dropped.connect(self._on_floating_drop)
        self.floating_widget.open_main_window_requested.connect(self._show_and_raise)

        # Drop Zones List
        self.drop_zones: List[DropZoneTile] = []
        self.nav_buttons: List[QPushButton] = []
        self.preset_buttons: Dict[str, QPushButton] = {}
        self.tray_icon: Optional[QSystemTrayIcon] = None

        self._init_ui()
        self._setup_system_tray()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar Navigation
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Right Content Stack
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 18, 20, 18)
        content_layout.setSpacing(14)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_mode1_page())
        self.stack.addWidget(self._build_mode2_page())
        self.stack.addWidget(self._build_rules_page())
        self.stack.addWidget(DuplicateCleanerWidget())
        self.stack.addWidget(HistoryUndoWidget(self.undo_manager))
        self.stack.addWidget(self._build_watcher_page())

        content_layout.addWidget(self.stack)
        root_layout.addWidget(content_container, 1)

        # Create MenuBar, ToolBar, and StatusBar after pages are constructed
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()

        # Set default active tab
        self._switch_nav(0)

    # ==========================================
    # MENUBAR, TOOLBAR & STATUSBAR
    # ==========================================
    def _create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # 1. File Menu
        file_menu = menubar.addMenu("&File")

        act_open = QAction("📁 &Open Folder to Organize...", self)
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._browse_source_folder)
        file_menu.addAction(act_open)

        act_dest = QAction("📍 Set &Destination Target...", self)
        act_dest.setShortcut(QKeySequence("Ctrl+D"))
        act_dest.triggered.connect(self._browse_custom_dest)
        file_menu.addAction(act_dest)

        file_menu.addSeparator()

        act_open_downloads = QAction("📥 Open &Downloads Directory", self)
        act_open_downloads.triggered.connect(lambda: self._open_dir(os.path.join(os.path.expanduser("~"), "Downloads")))
        file_menu.addAction(act_open_downloads)

        act_open_desktop = QAction("🖥️ Open Des&ktop Directory", self)
        act_open_desktop.triggered.connect(lambda: self._open_dir(os.path.join(os.path.expanduser("~"), "Desktop")))
        file_menu.addAction(act_open_desktop)

        act_reveal = QAction("↗ Reveal Current Folder in &Explorer", self)
        act_reveal.setShortcut(QKeySequence("Ctrl+E"))
        act_reveal.triggered.connect(self._open_in_explorer)
        file_menu.addAction(act_reveal)

        file_menu.addSeparator()

        act_exit = QAction("🚪 E&xit", self)
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # 2. Actions Menu
        act_menu = menubar.addMenu("&Actions")

        act_sim = QAction("🔍 &Simulate & Preview (Dry Run)", self)
        act_sim.setShortcut(QKeySequence("F5"))
        act_sim.triggered.connect(self._generate_mode1_preview)
        act_menu.addAction(act_sim)

        act_run = QAction("🚀 &Run Organization Now", self)
        act_run.setShortcut(QKeySequence("Ctrl+Return"))
        act_run.triggered.connect(self._run_mode1_execution)
        act_menu.addAction(act_run)

        act_menu.addSeparator()

        act_sel_all = QAction("Select &All Items", self)
        act_sel_all.setShortcut(QKeySequence("Ctrl+A"))
        act_sel_all.triggered.connect(lambda: self._set_all_preview_selected(True))
        act_menu.addAction(act_sel_all)

        act_desel_all = QAction("&Deselect All Items", self)
        act_desel_all.setShortcut(QKeySequence("Ctrl+Shift+A"))
        act_desel_all.triggered.connect(lambda: self._set_all_preview_selected(False))
        act_menu.addAction(act_desel_all)

        act_menu.addSeparator()

        act_undo = QAction("⏪ &Undo / Rollback Last Batch", self)
        act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        act_undo.triggered.connect(self._undo_last_batch)
        act_menu.addAction(act_undo)

        act_menu.addSeparator()

        act_dups = QAction("🔎 Scan for &Duplicates...", self)
        act_dups.setShortcut(QKeySequence("Ctrl+Shift+D"))
        act_dups.triggered.connect(lambda: self._switch_nav(3))
        act_menu.addAction(act_dups)

        # 3. Rules Menu
        rules_menu = menubar.addMenu("&Rules")

        act_new_rule = QAction("+ &Create New Automation Rule...", self)
        act_new_rule.setShortcut(QKeySequence("Ctrl+N"))
        act_new_rule.triggered.connect(self._create_new_rule)
        rules_menu.addAction(act_new_rule)

        act_test_rule = QAction("🧪 &Test Rule on Sample File...", self)
        act_test_rule.setShortcut(QKeySequence("Ctrl+T"))
        act_test_rule.triggered.connect(self._test_rule_on_file)
        rules_menu.addAction(act_test_rule)

        rules_menu.addSeparator()

        act_def_rules = QAction("🔄 Reset to &Default Rules", self)
        act_def_rules.triggered.connect(self._reset_default_rules)
        rules_menu.addAction(act_def_rules)

        # 4. Watcher Menu
        watcher_menu = menubar.addMenu("&Watcher")

        act_start_watch = QAction("▶ &Start Background Watcher", self)
        act_start_watch.setShortcut(QKeySequence("F9"))
        act_start_watch.triggered.connect(lambda: self._toggle_watcher_state(True))
        watcher_menu.addAction(act_start_watch)

        act_stop_watch = QAction("⏹ S&top Background Watcher", self)
        act_stop_watch.setShortcut(QKeySequence("F10"))
        act_stop_watch.triggered.connect(lambda: self._toggle_watcher_state(False))
        watcher_menu.addAction(act_stop_watch)

        watcher_menu.addSeparator()

        act_add_watch = QAction("+ &Add Folder to Monitor...", self)
        act_add_watch.triggered.connect(self._add_watch_folder)
        watcher_menu.addAction(act_add_watch)

        act_clear_log = QAction("🧹 Clear Live &Activity Log", self)
        act_clear_log.triggered.connect(self.list_watcher_log.clear)
        watcher_menu.addAction(act_clear_log)

        # 5. View Menu
        view_menu = menubar.addMenu("&View")

        nav_actions = [
            ("📁 Folder Auto-Cleaner Mode", "Ctrl+1", 0),
            ("🎯 Instant Drop Zones Hub", "Ctrl+2", 1),
            ("⚙️ Automation Rules Pipeline", "Ctrl+3", 2),
            ("🔍 Duplicate Cleaner", "Ctrl+4", 3),
            ("📜 History & Undo", "Ctrl+5", 4),
            ("📡 Folder Watcher", "Ctrl+6", 5),
        ]
        for name, shortcut, idx in nav_actions:
            act = QAction(name, self)
            act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(lambda _, i=idx: self._switch_nav(i))
            view_menu.addAction(act)

        view_menu.addSeparator()

        act_float_target = QAction("📌 Toggle &Floating Mini-Target", self)
        act_float_target.setShortcut(QKeySequence("F8"))
        act_float_target.triggered.connect(self._toggle_floating_widget)
        view_menu.addAction(act_float_target)

        # 6. Help Menu
        help_menu = menubar.addMenu("&Help")

        act_guide = QAction("📖 &Quick Start & Features Guide", self)
        act_guide.setShortcut(QKeySequence("F1"))
        act_guide.triggered.connect(self._show_guide_dialog)
        help_menu.addAction(act_guide)

        help_menu.addSeparator()

        act_about = QAction("ℹ️ &About Titus OmniSort Pro...", self)
        act_about.triggered.connect(self._show_about_dialog)
        help_menu.addAction(act_about)

    def _create_tool_bar(self):
        toolbar = QToolBar("Main Navigation Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Quick action tool buttons
        btn_open = QAction("📁 Open Folder", self)
        btn_open.setToolTip("Browse a messy folder to clean and categorize (Ctrl+O)")
        btn_open.triggered.connect(self._browse_source_folder)
        toolbar.addAction(btn_open)

        btn_sim = QAction("🔍 Preview", self)
        btn_sim.setToolTip("Run simulation and preview proposed changes without touching files (F5)")
        btn_sim.triggered.connect(self._generate_mode1_preview)
        toolbar.addAction(btn_sim)

        btn_run = QAction("🚀 Run Sort", self)
        btn_run.setToolTip("Execute approved organization actions (Ctrl+Enter)")
        btn_run.triggered.connect(self._run_mode1_execution)
        toolbar.addAction(btn_run)

        btn_undo = QAction("⏪ Undo Last", self)
        btn_undo.setToolTip("1-Click rollback of previous sorting session (Ctrl+Z)")
        btn_undo.triggered.connect(self._undo_last_batch)
        toolbar.addAction(btn_undo)

        toolbar.addSeparator()

        btn_zones = QAction("🎯 Drop Zones", self)
        btn_zones.setToolTip("Switch to Instant Drag-and-Drop Drop Zones Hub (Ctrl+2)")
        btn_zones.triggered.connect(lambda: self._switch_nav(1))
        toolbar.addAction(btn_zones)

        btn_dups = QAction("🔎 Duplicates", self)
        btn_dups.setToolTip("Scan and clean duplicate files (Ctrl+Shift+D)")
        btn_dups.triggered.connect(lambda: self._switch_nav(3))
        toolbar.addAction(btn_dups)

        btn_rules = QAction("⚙️ Rules", self)
        btn_rules.setToolTip("Manage File Juggler automation rules (Ctrl+3)")
        btn_rules.triggered.connect(lambda: self._switch_nav(2))
        toolbar.addAction(btn_rules)

        toolbar.addSeparator()

        btn_float = QAction("📌 Float Target", self)
        btn_float.setToolTip("Toggle desktop floating always-on-top drop target (F8)")
        btn_float.triggered.connect(self._toggle_floating_widget)
        toolbar.addAction(btn_float)

        btn_watcher = QAction("📡 Watcher", self)
        btn_watcher.setToolTip("Toggle background folder monitor (F9)")
        btn_watcher.triggered.connect(self._toggle_watcher)
        toolbar.addAction(btn_watcher)

        # Spacer to push status label to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.lbl_toolbar_hint = QLabel("Ready")
        self.lbl_toolbar_hint.setStyleSheet("color: #94a3b8; font-size: 11px; padding-right: 12px; font-weight: 500;")
        toolbar.addWidget(self.lbl_toolbar_hint)

    def _create_status_bar(self):
        statusbar = self.statusBar()
        statusbar.showMessage("Ready. Drag a messy folder into the app or select an action from the toolbar.")

        self.status_folder = QLabel("📁 No Folder Selected")
        self.status_folder.setStyleSheet("color: #60a5fa; font-weight: 600; padding: 0 10px;")
        statusbar.addPermanentWidget(self.status_folder)

        self.status_watcher = QLabel("⏹ Watcher: Off")
        self.status_watcher.setStyleSheet("color: #94a3b8; padding: 0 10px;")
        statusbar.addPermanentWidget(self.status_watcher)

        self.status_undo_count = QLabel("⏪ History: 0 Batches")
        self.status_undo_count.setStyleSheet("color: #a78bfa; padding: 0 10px;")
        statusbar.addPermanentWidget(self.status_undo_count)
        self._refresh_status_undo()

    # ==========================================
    # LEFT NAVIGATION SIDEBAR
    # ==========================================
    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0d1017;
                border-right: 1px solid #1a202e;
            }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 18, 10, 16)
        layout.setSpacing(4)

        # Brand Header
        brand_frame = QFrame()
        brand_frame.setStyleSheet("background: transparent; border: none; padding-left: 6px; margin-bottom: 12px;")
        b_layout = QVBoxLayout(brand_frame)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(4)

        title_h = QHBoxLayout()
        lbl_brand_icon = QLabel()
        lbl_brand_icon.setPixmap(get_app_pixmap(28))
        lbl_brand_icon.setFixedSize(30, 30)
        title_h.addWidget(lbl_brand_icon)

        lbl_brand_title = QLabel("Titus OmniSort")
        lbl_brand_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fafc; letter-spacing: -0.3px;")
        title_h.addWidget(lbl_brand_title)

        lbl_pro_badge = QLabel("PRO")
        lbl_pro_badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
            color: #ffffff;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 6px;
        """)
        title_h.addWidget(lbl_pro_badge)
        title_h.addStretch()
        b_layout.addLayout(title_h)

        lbl_brand_desc = QLabel("2-in-1 Folder & File Intelligent Sorter")
        lbl_brand_desc.setStyleSheet("font-size: 10px; color: #64748b; font-weight: 500;")
        b_layout.addWidget(lbl_brand_desc)

        layout.addWidget(brand_frame)

        # Navigation items
        nav_items = [
            ("📁  Folder Auto-Cleaner", 0),
            ("🎯  Instant Drop Zones", 1),
            ("⚙️  Automation Rules", 2),
            ("🔍  Duplicate Cleaner", 3),
            ("📜  History & Undo", 4),
            ("📡  Folder Watcher", 5),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "navBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=index: self._switch_nav(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # Bottom Utilities Box
        bottom_box = QFrame()
        bottom_box.setStyleSheet("""
            QFrame {
                background-color: #121622;
                border: 1px solid #1e2638;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        bot_layout = QVBoxLayout(bottom_box)
        bot_layout.setContentsMargins(6, 6, 6, 6)
        bot_layout.setSpacing(8)

        self.btn_toggle_float = QPushButton("📌 Float Mini-Target")
        self.btn_toggle_float.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_float.setStyleSheet("""
            QPushButton {
                background-color: #1a2233;
                border: 1px solid #2b3954;
                color: #93c5fd;
                font-size: 11px;
                padding: 7px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #243048;
                border-color: #6366f1;
                color: #ffffff;
            }
        """)
        self.btn_toggle_float.clicked.connect(self._toggle_floating_widget)
        bot_layout.addWidget(self.btn_toggle_float)

        self.lbl_watcher_badge = QLabel("⏹ Watcher Inactive")
        self.lbl_watcher_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_watcher_badge.setStyleSheet("""
            color: #94a3b8;
            background-color: #151b27;
            padding: 5px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        """)
        bot_layout.addWidget(self.lbl_watcher_badge)

        layout.addWidget(bottom_box)
        return sidebar

    def _switch_nav(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 11px 16px;
                        font-size: 13px;
                        font-weight: 700;
                        color: #ffffff;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #182032, stop:1 #222b40);
                        border: 1px solid #2f3b55;
                        border-left: 3px solid #6366f1;
                        border-radius: 8px;
                        margin: 2px 6px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 11px 16px;
                        font-size: 13px;
                        font-weight: 600;
                        color: #94a3b8;
                        background-color: transparent;
                        border: 1px solid transparent;
                        border-radius: 8px;
                        margin: 2px 6px;
                    }
                    QPushButton:hover {
                        background-color: #141926;
                        color: #f8fafc;
                        border: 1px solid #232c3f;
                    }
                """)

    # ==========================================
    # PAGE 1: FOLDER AUTO-CLEANER (Mode 1)
    # ==========================================
    def _build_mode1_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Page Title
        lbl_head = QLabel("Batch Folder Auto-Cleaner")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(lbl_head)

        # Large Hero Drop Zone Banner
        self.hero_drop_frame = QFrame()
        self.hero_drop_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hero_drop_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121622, stop:1 #0e121c);
                border: 2px dashed #333f58;
                border-radius: 12px;
                padding: 18px;
            }
            QFrame:hover {
                border-color: #6366f1;
                background-color: #141926;
            }
        """)
        hero_layout = QVBoxLayout(self.hero_drop_frame)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.setSpacing(8)

        lbl_icon = QLabel("📂")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 38px; color: #818cf8;")
        hero_layout.addWidget(lbl_icon)

        self.lbl_hero_title = QLabel("Drag & Drop Any Messy Folder Here")
        self.lbl_hero_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hero_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        hero_layout.addWidget(self.lbl_hero_title)

        self.lbl_hero_sub = QLabel("Select messy folders like Downloads or Desktop to analyze and reorganize")
        self.lbl_hero_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hero_sub.setStyleSheet("font-size: 12px; color: #94a3b8;")
        hero_layout.addWidget(self.lbl_hero_sub)

        btn_browse_folder = QPushButton("📁 Browse Directory...")
        btn_browse_folder.setFixedWidth(180)
        btn_browse_folder.setStyleSheet("""
            QPushButton {
                background-color: #1e2638;
                border: 1px solid #3b4764;
                color: #e2e8f0;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2b364e;
                border-color: #6366f1;
                color: #ffffff;
            }
        """)
        btn_browse_folder.clicked.connect(self._browse_source_folder)
        hero_layout.addWidget(btn_browse_folder, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.hero_drop_frame)

        # Dynamic Metrics HUD (Hidden until folder selected)
        self.hud_frame = QFrame()
        self.hud_frame.setVisible(False)
        self.hud_frame.setStyleSheet("background-color: #111520; border: 1px solid #1e2638; border-radius: 10px; padding: 10px;")
        hud_layout = QHBoxLayout(self.hud_frame)
        hud_layout.setContentsMargins(12, 8, 12, 8)
        hud_layout.setSpacing(16)

        # KPI 1: Total Files
        self.kpi_files = QLabel("0 Files")
        self.kpi_files.setStyleSheet("font-size: 15px; font-weight: 800; color: #60a5fa;")
        hud_layout.addWidget(self._make_kpi_card("📄 Total Files", self.kpi_files))

        # KPI 2: Total Size
        self.kpi_size = QLabel("0 MB")
        self.kpi_size.setStyleSheet("font-size: 15px; font-weight: 800; color: #34d399;")
        hud_layout.addWidget(self._make_kpi_card("💾 Total Size", self.kpi_size))

        # KPI 3: Category breakdown chips
        self.kpi_chips = QLabel("No files")
        self.kpi_chips.setStyleSheet("font-size: 12px; color: #cbd5e1; font-weight: 600;")
        hud_layout.addWidget(self._make_kpi_card("🏷️ Top File Types", self.kpi_chips), 1)

        layout.addWidget(self.hud_frame)

        # Smart Presets Pill Selector
        presets_box = QFrame()
        presets_box.setStyleSheet("background-color: #111520; border: 1px solid #1e2638; border-radius: 10px; padding: 12px;")
        p_layout = QVBoxLayout(presets_box)
        p_layout.setSpacing(10)

        lbl_preset_title = QLabel("Choose Organization Mode / Preset:")
        lbl_preset_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;")
        p_layout.addWidget(lbl_preset_title)

        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(8)

        preset_options = [
            ("🌟 Category", "category"),
            ("🏷️ Extension", "extension"),
            ("📅 Year/Month", "year_month"),
            ("📆 Year Only", "year"),
            ("📏 File Size", "size"),
            ("🔤 A - Z", "alphabetical"),
            ("⚡ Custom Rules", "rules")
        ]

        for label, val in preset_options:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, v=val: self._select_preset(v))
            self.preset_buttons[val] = btn
            pills_layout.addWidget(btn)

        p_layout.addLayout(pills_layout)

        # Destination & Action Row
        dest_h = QHBoxLayout()
        dest_h.setSpacing(14)

        self.radio_inplace = QRadioButton("In-Place Subfolders")
        self.radio_inplace.setChecked(True)
        self.radio_dest = QRadioButton("Sort into Specific Directory:")
        self.btn_group_dest = QButtonGroup(self)
        self.btn_group_dest.addButton(self.radio_inplace)
        self.btn_group_dest.addButton(self.radio_dest)
        dest_h.addWidget(self.radio_inplace)
        dest_h.addWidget(self.radio_dest)

        self.txt_custom_dest = QLabel("(Select target folder)")
        self.txt_custom_dest.setStyleSheet("color: #93c5fd; font-size: 11px;")
        dest_h.addWidget(self.txt_custom_dest)

        self.btn_pick_dest = QPushButton("Browse...")
        self.btn_pick_dest.clicked.connect(self._browse_custom_dest)
        self.btn_pick_dest.setEnabled(False)
        self.radio_dest.toggled.connect(self.btn_pick_dest.setEnabled)
        dest_h.addWidget(self.btn_pick_dest)

        dest_h.addStretch()

        self.chk_copy = QCheckBox("Copy files (preserve original)")
        dest_h.addWidget(self.chk_copy)

        btn_sim = QPushButton("🔍 Simulate & Preview")
        btn_sim.setObjectName("btnPrimary")
        btn_sim.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sim.clicked.connect(self._generate_mode1_preview)
        dest_h.addWidget(btn_sim)

        p_layout.addLayout(dest_h)
        layout.addWidget(presets_box)

        # Highlight default preset button
        self._select_preset("category")

        # Preview Data Table
        self.table_preview = QTableWidget()
        self.table_preview.setColumnCount(7)
        self.table_preview.setHorizontalHeaderLabels([
            "Select", "File Name", "Original Source", "Planned Destination", "Category", "Size", "Status"
        ])
        self.table_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_preview.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_preview.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_preview, 1)

        # Execution Action Bar
        exec_bar = QHBoxLayout()
        exec_bar.setSpacing(10)

        btn_select_all = QPushButton("Select All")
        btn_select_all.clicked.connect(lambda: self._set_all_preview_selected(True))
        exec_bar.addWidget(btn_select_all)

        btn_deselect_all = QPushButton("Deselect All")
        btn_deselect_all.clicked.connect(lambda: self._set_all_preview_selected(False))
        exec_bar.addWidget(btn_deselect_all)

        exec_bar.addStretch()

        self.lbl_exec_status = QLabel("")
        self.lbl_exec_status.setStyleSheet("color: #34d399; font-weight: 700; font-size: 12px;")
        exec_bar.addWidget(self.lbl_exec_status)

        self.btn_execute = QPushButton("🚀 Run Organization Now")
        self.btn_execute.setObjectName("btnSuccess")
        self.btn_execute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_execute.clicked.connect(self._run_mode1_execution)
        self.btn_execute.setEnabled(False)
        exec_bar.addWidget(self.btn_execute)

        layout.addLayout(exec_bar)

        self.progress_mode1 = QProgressBar()
        self.progress_mode1.setVisible(False)
        layout.addWidget(self.progress_mode1)

        return widget

    def _make_kpi_card(self, title: str, value_label: QLabel) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 600;")
        layout.addWidget(lbl)
        layout.addWidget(value_label)
        return card

    def _select_preset(self, preset_val: str):
        self.selected_preset = preset_val
        for val, btn in self.preset_buttons.items():
            if val == preset_val:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #6366f1);
                        color: #ffffff;
                        border: 1px solid #818cf8;
                        border-radius: 7px;
                        font-weight: 700;
                        padding: 7px 14px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #171c28;
                        color: #94a3b8;
                        border: 1px solid #283248;
                        border-radius: 7px;
                        font-weight: 600;
                        padding: 7px 14px;
                    }
                    QPushButton:hover {
                        background-color: #21293a;
                        color: #f8fafc;
                        border-color: #435275;
                    }
                """)

    # ==========================================
    # PAGE 2: INSTANT DROP ZONES HUB (Mode 2)
    # ==========================================
    def _build_mode2_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header
        top_h = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        lbl_head = QLabel("Instant Drop Zones Hub")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        header_text.addWidget(lbl_head)

        lbl_sub = QLabel("Drag files directly onto any bucket tile below to instantly sort them.")
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header_text.addWidget(lbl_sub)
        top_h.addLayout(header_text)

        top_h.addStretch()

        btn_add_zone = QPushButton("+ Add Custom Drop Zone")
        btn_add_zone.setObjectName("btnPrimary")
        btn_add_zone.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_zone.clicked.connect(self._add_custom_drop_zone)
        top_h.addWidget(btn_add_zone)
        layout.addLayout(top_h)

        # Scrollable Grid of Drop Zone Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.grid_zones = QGridLayout(container)
        self.grid_zones.setSpacing(14)
        self.grid_zones.setContentsMargins(4, 4, 4, 4)

        user_home = os.path.expanduser("~")
        defaults = [
            ("zone_docs", "Documents & PDFs", os.path.join(user_home, "Documents"), "📄", "#3b82f6"),
            ("zone_pics", "Photos & Images", os.path.join(user_home, "Pictures"), "🖼️", "#ec4899"),
            ("zone_finance", "Receipts & Invoices", os.path.join(user_home, "Documents", "Receipts"), "🧾", "#10b981"),
            ("zone_audio", "Music & Audio", os.path.join(user_home, "Music"), "🎵", "#8b5cf6"),
            ("zone_video", "Videos & Movies", os.path.join(user_home, "Videos"), "🎬", "#f59e0b"),
            ("zone_archives", "Archives & Zips", os.path.join(user_home, "Downloads", "Archives"), "📦", "#6366f1"),
            ("zone_code", "Code & Dev Projects", os.path.join(user_home, "Documents", "Projects"), "💻", "#06b6d4"),
            ("zone_installers", "Installers & Setups", os.path.join(user_home, "Downloads", "Installers"), "⚙️", "#e11d48"),
        ]

        row, col = 0, 0
        for zid, title, path, icon, color in defaults:
            tile = DropZoneTile(zid, title, path, icon=icon, color_accent=color)
            tile.files_dropped.connect(self._on_zone_drop)
            self.drop_zones.append(tile)
            self.grid_zones.addWidget(tile, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        return widget

    # ==========================================
    # PAGE 3: AUTOMATION RULES (File Juggler)
    # ==========================================
    def _build_rules_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        top_h = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_head = QLabel("File Juggler Automation Rules Pipeline")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        header_text.addWidget(lbl_head)

        lbl_sub = QLabel("Conditional automation rules for deep content inspection (PDF text, Word docs, EXIF).")
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header_text.addWidget(lbl_sub)
        top_h.addLayout(header_text)

        top_h.addStretch()

        btn_new_rule = QPushButton("+ Create New Rule")
        btn_new_rule.setObjectName("btnPrimary")
        btn_new_rule.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_rule.clicked.connect(self._create_new_rule)
        top_h.addWidget(btn_new_rule)

        layout.addLayout(top_h)

        # Rules Table
        self.table_rules = QTableWidget()
        self.table_rules.setColumnCount(5)
        self.table_rules.setHorizontalHeaderLabels(["Status", "Rule Name", "Conditions", "Action", "Target Folder Template"])
        self.table_rules.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_rules.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_rules.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_rules.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_rules.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table_rules, 1)

        # Bottom actions
        btn_row = QHBoxLayout()
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_edit.clicked.connect(self._edit_selected_rule)
        btn_row.addWidget(btn_edit)

        btn_del = QPushButton("🗑️ Delete Rule")
        btn_del.clicked.connect(self._delete_selected_rule)
        btn_row.addWidget(btn_del)

        btn_test = QPushButton("🧪 Test Rule on File...")
        btn_test.clicked.connect(self._test_rule_on_file)
        btn_row.addWidget(btn_test)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._refresh_rules_table()
        return widget

    # ==========================================
    # PAGE 6: BACKGROUND WATCHER (File Juggler)
    # ==========================================
    def _build_watcher_page(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header_h = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_head = QLabel("Real-Time Directory Monitor & Auto-Watcher")
        lbl_head.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        header_text.addWidget(lbl_head)

        lbl_sub = QLabel("Continuously monitors incoming files and automatically routes them when downloads settle.")
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        header_text.addWidget(lbl_sub)
        header_h.addLayout(header_text)

        header_h.addStretch()

        self.btn_toggle_watcher = QPushButton("▶ Start Background Watcher")
        self.btn_toggle_watcher.setObjectName("btnSuccess")
        self.btn_toggle_watcher.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_watcher.clicked.connect(self._toggle_watcher)
        header_h.addWidget(self.btn_toggle_watcher)

        layout.addLayout(header_h)

        # Monitored Folders Frame
        watch_frame = QFrame()
        watch_frame.setStyleSheet("background-color: #111520; border: 1px solid #1e2638; border-radius: 10px; padding: 12px;")
        w_layout = QVBoxLayout(watch_frame)
        w_layout.setSpacing(8)

        bar_h = QHBoxLayout()
        lbl_w = QLabel("Monitored Directories:")
        lbl_w.setStyleSheet("font-weight: 700; color: #e2e8f0;")
        bar_h.addWidget(lbl_w)
        bar_h.addStretch()

        btn_add_watch = QPushButton("+ Add Folder...")
        btn_add_watch.clicked.connect(self._add_watch_folder)
        bar_h.addWidget(btn_add_watch)

        btn_rem_watch = QPushButton("- Remove Folder")
        btn_rem_watch.clicked.connect(self._remove_watch_folder)
        bar_h.addWidget(btn_rem_watch)
        w_layout.addLayout(bar_h)

        self.list_watched = QListWidget()
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads_dir):
            self.list_watched.addItem(downloads_dir)
            self.watcher.add_watch_path(downloads_dir)
        w_layout.addWidget(self.list_watched)

        # Delay settings
        delay_h = QHBoxLayout()
        delay_h.addWidget(QLabel("Download stabilization settling delay:"))
        self.spin_settle = QSpinBox()
        self.spin_settle.setRange(1, 60)
        self.spin_settle.setValue(3)
        self.spin_settle.setSuffix(" seconds")
        self.spin_settle.valueChanged.connect(lambda v: setattr(self.watcher, 'settle_seconds', float(v)))
        delay_h.addWidget(self.spin_settle)
        delay_h.addStretch()
        w_layout.addLayout(delay_h)

        layout.addWidget(watch_frame)

        # Activity Log Frame
        log_frame = QFrame()
        log_frame.setStyleSheet("background-color: #111520; border: 1px solid #1e2638; border-radius: 10px; padding: 12px;")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setSpacing(8)

        lbl_log = QLabel("Live Auto-Sort Activity Log:")
        lbl_log.setStyleSheet("font-weight: 700; color: #e2e8f0;")
        log_layout.addWidget(lbl_log)

        self.list_watcher_log = QListWidget()
        log_layout.addWidget(self.list_watcher_log, 1)

        layout.addWidget(log_frame, 1)

        return widget

    # ==========================================
    # LOGIC & EVENT HANDLERS
    # ==========================================
    def _browse_source_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Select Messy Folder to Organize")
        if f:
            self._load_source_folder(os.path.abspath(f))

    def _browse_custom_dest(self):
        f = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if f:
            self.txt_custom_dest.setText(os.path.abspath(f))

    def _load_source_folder(self, folder_path: str):
        self.current_source_folder = folder_path
        self.lbl_hero_title.setText(f"Folder Loaded: {os.path.basename(folder_path) or folder_path}")
        self.lbl_hero_sub.setText(folder_path)
        self.hud_frame.setVisible(True)

        total_files = 0
        total_size = 0
        category_counts: Dict[str, int] = {}

        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    fp = os.path.join(root, file)
                    try:
                        sz = os.path.getsize(fp)
                        cat = get_file_category(file)
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                        total_files += 1
                        total_size += sz
                    except OSError:
                        pass
        except OSError:
            pass

        self.kpi_files.setText(f"{total_files:,} Files")
        self.kpi_size.setText(format_file_size(total_size))

        chips = []
        for cat, cnt in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            icon = CATEGORY_ICONS.get(cat, '📁')
            chips.append(f"{icon} {cat}: {cnt}")

        self.kpi_chips.setText("  •  ".join(chips) if chips else "Empty folder")

        # Update StatusBar & ToolBar
        disp = os.path.basename(folder_path) or folder_path
        if hasattr(self, 'status_folder'):
            self.status_folder.setText(f"📂 {disp}")
        if hasattr(self, 'lbl_toolbar_hint'):
            self.lbl_toolbar_hint.setText(f"Loaded: {disp} ({total_files:,} items)")
        self.statusBar().showMessage(f"Loaded '{disp}': {total_files:,} files totaling {format_file_size(total_size)}.", 4000)

    def _generate_mode1_preview(self):
        if not self.current_source_folder or not os.path.isdir(self.current_source_folder):
            QMessageBox.warning(self, "No Folder", "Please choose or drop a folder first.")
            return

        preset = self.selected_preset
        action = 'copy' if self.chk_copy.isChecked() else 'move'

        dest_root = None
        if self.radio_dest.isChecked():
            dest_text = self.txt_custom_dest.text()
            if os.path.isdir(dest_text):
                dest_root = dest_text
            else:
                QMessageBox.warning(self, "Destination Missing", "Please select a valid destination folder.")
                return

        all_files = []
        for root, _, files in os.walk(self.current_source_folder):
            for f in files:
                all_files.append(os.path.join(root, f))

        self.planned_operations = self.engine.generate_preview(
            file_paths=all_files,
            preset_mode=preset,
            destination_root=dest_root,
            action=action,
            conflict_mode='rename_new'
        )

        self._populate_preview_table(self.planned_operations)
        self.btn_execute.setEnabled(len(self.planned_operations) > 0)
        self.lbl_exec_status.setText(f"Generated {len(self.planned_operations)} planned actions. Review below.")

    def _populate_preview_table(self, ops: List[PlannedFileOperation]):
        self.table_preview.setRowCount(len(ops))
        for row, op in enumerate(ops):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(chk_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(Qt.CheckState.Checked if op.selected else Qt.CheckState.Unchecked)
            self.table_preview.setItem(row, 0, chk_item)

            filename = os.path.basename(op.source_path)
            self.table_preview.setItem(row, 1, QTableWidgetItem(filename))
            self.table_preview.setItem(row, 2, QTableWidgetItem(op.source_path))
            self.table_preview.setItem(row, 3, QTableWidgetItem(op.target_path))
            self.table_preview.setItem(row, 4, QTableWidgetItem(op.category))
            self.table_preview.setItem(row, 5, QTableWidgetItem(format_file_size(op.file_size)))
            self.table_preview.setItem(row, 6, QTableWidgetItem(op.status))

    def _set_all_preview_selected(self, select: bool):
        for row in range(self.table_preview.rowCount()):
            item = self.table_preview.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked if select else Qt.CheckState.Unchecked)
        for op in self.planned_operations:
            op.selected = select

    def _run_mode1_execution(self):
        for row, op in enumerate(self.planned_operations):
            item = self.table_preview.item(row, 0)
            if item:
                op.selected = (item.checkState() == Qt.CheckState.Checked)

        selected_ops = [op for op in self.planned_operations if op.selected]
        if not selected_ops:
            QMessageBox.information(self, "No Files Selected", "Please select at least one file to organize.")
            return

        self.btn_execute.setEnabled(False)
        self.progress_mode1.setVisible(True)
        self.progress_mode1.setMaximum(len(selected_ops))
        self.progress_mode1.setValue(0)

        desc = f"Mode 1 Organize ({self.selected_preset})"
        self._exec_worker = ExecutionWorker(
            engine=self.engine,
            ops=self.planned_operations,
            desc=desc,
            root=self.current_source_folder
        )
        self._exec_worker.progress.connect(self._on_exec_progress)
        self._exec_worker.finished_exec.connect(self._on_exec_finished)
        self._exec_worker.start()

    def _on_exec_progress(self, cur: int, total: int, msg: str):
        self.progress_mode1.setValue(cur)
        self.lbl_exec_status.setText(f"Organizing ({cur}/{total}): {msg}")

    def _on_exec_finished(self, res: dict):
        self.progress_mode1.setVisible(False)
        self.btn_execute.setEnabled(True)

        for row, op in enumerate(self.planned_operations):
            item = self.table_preview.item(row, 6)
            if item:
                item.setText(op.status)

        msg = f"Successfully sorted {res['completed']} files!"
        if res.get('errors'):
            msg += f"\nEncountered {len(res['errors'])} errors."
        QMessageBox.information(self, "Organization Finished", msg)
        self.lbl_exec_status.setText("Organization completed! You can undo anytime from History & Undo.")

        if self.current_source_folder:
            self._load_source_folder(self.current_source_folder)

    # Mode 2 Drop Handlers
    def _on_zone_drop(self, file_paths: List[str], target_dir: str):
        if not file_paths:
            return

        os.makedirs(target_dir, exist_ok=True)
        ops = self.engine.generate_preview(
            file_paths=file_paths,
            preset_mode='direct_target',
            direct_target_folder=target_dir,
            action='move'
        )
        if not ops:
            QMessageBox.information(self, "Notice", "All dropped files are already in the target folder.")
            return

        res = self.engine.execute_operations(
            operations=ops,
            batch_description=f"Drop Zone Sort to {os.path.basename(target_dir)}",
            source_root="Instant Drop Zone"
        )
        for tile in self.drop_zones:
            if tile.target_dir == target_dir:
                tile.increment_count(res['completed'])

        QMessageBox.information(
            self, 
            "Drop Sorted", 
            f"Instantly sorted {res['completed']} files into:\n{target_dir}"
        )

    def _add_custom_drop_zone(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder for New Drop Zone")
        if folder:
            name = os.path.basename(folder) or "Custom Zone"
            zid = f"zone_custom_{len(self.drop_zones)}"
            tile = DropZoneTile(zid, name, folder, icon="⭐", color_accent="#10b981")
            tile.files_dropped.connect(self._on_zone_drop)
            self.drop_zones.append(tile)

            idx = len(self.drop_zones) - 1
            row = idx // 3
            col = idx % 3
            self.grid_zones.addWidget(tile, row, col)

    # Floating Widget
    def _toggle_floating_widget(self):
        if self.floating_widget.isVisible():
            self.floating_widget.hide()
            self.btn_toggle_float.setText("📌 Float Mini-Target")
        else:
            self.floating_widget.show()
            self.btn_toggle_float.setText("📌 Hide Mini-Target")

    def _show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_floating_drop(self, files: List[str], mode_str: str):
        preset = 'category'
        dest = None
        if "Documents" in mode_str:
            preset = 'direct_target'
            dest = os.path.join(os.path.expanduser("~"), "Documents")
        elif "Pictures" in mode_str:
            preset = 'direct_target'
            dest = os.path.join(os.path.expanduser("~"), "Pictures")
        elif "Rules" in mode_str:
            preset = 'rules'

        ops = self.engine.generate_preview(
            file_paths=files,
            preset_mode=preset,
            direct_target_folder=dest,
            action='move'
        )
        if ops:
            res = self.engine.execute_operations(
                operations=ops,
                batch_description="Floating Widget Drop",
                source_root="Floating Drop"
            )
            self.lbl_exec_status.setText(f"Floating Drop: Sorted {res['completed']} files.")

    # Rules tab
    def _refresh_rules_table(self):
        rules = self.rule_engine.rules
        self.table_rules.setRowCount(len(rules))
        for row, r in enumerate(rules):
            chk = QTableWidgetItem("Active" if r.enabled else "Disabled")
            chk.setForeground(Qt.GlobalColor.green if r.enabled else Qt.GlobalColor.gray)
            self.table_rules.setItem(row, 0, chk)
            self.table_rules.setItem(row, 1, QTableWidgetItem(r.name))

            cond_strs = [f"{c.field} {c.operator} '{c.value}'" for c in r.conditions]
            joiner = " AND " if r.match_all else " OR "
            self.table_rules.setItem(row, 2, QTableWidgetItem(joiner.join(cond_strs)))

            self.table_rules.setItem(row, 3, QTableWidgetItem(r.action.action_type.upper()))
            self.table_rules.setItem(row, 4, QTableWidgetItem(r.action.target_folder))

    def _create_new_rule(self):
        dlg = RuleDialog(parent=self)
        if dlg.exec():
            self.rule_engine.add_rule(dlg.saved_rule)
            self._refresh_rules_table()

    def _edit_selected_rule(self):
        rows = self.table_rules.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        rule = self.rule_engine.rules[row]
        dlg = RuleDialog(rule, parent=self)
        if dlg.exec():
            self.rule_engine.rules[row] = dlg.saved_rule
            self.rule_engine.save()
            self._refresh_rules_table()

    def _delete_selected_rule(self):
        rows = self.table_rules.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        rule = self.rule_engine.rules[row]
        self.rule_engine.remove_rule(rule.id)
        self._refresh_rules_table()

    def _test_rule_on_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose a Sample File to Test Rules Against")
        if not file_path:
            return
        matched_rule = self.rule_engine.find_matching_rule(file_path)
        if matched_rule:
            QMessageBox.information(
                self, 
                "Rule Matched!", 
                f"File: {os.path.basename(file_path)}\n\nMatched Rule: {matched_rule.name}\nAction: {matched_rule.action.action_type.upper()}\nTarget Template: {matched_rule.action.target_folder}"
            )
        else:
            QMessageBox.information(
                self, 
                "No Match", 
                f"File: {os.path.basename(file_path)}\n\nDid not match any enabled rules."
            )

    # Watcher tab
    def _toggle_watcher(self):
        if self.watcher.active:
            self.watcher.stop()
            self.btn_toggle_watcher.setText("▶ Start Background Watcher")
            self.btn_toggle_watcher.setObjectName("btnSuccess")
            self.lbl_watcher_badge.setText("⏹ Watcher Inactive")
            self.lbl_watcher_badge.setStyleSheet("color: #94a3b8; background-color: #151b27; padding: 5px; border-radius: 6px; font-size: 11px; font-weight: 600;")
            if hasattr(self, 'status_watcher'):
                self.status_watcher.setText("⏹ Watcher: Off")
                self.status_watcher.setStyleSheet("color: #94a3b8; padding: 0 10px;")
            self.statusBar().showMessage("Background Watcher stopped.", 3000)
        else:
            self.watcher.start()
            self.btn_toggle_watcher.setText("⏹ Stop Background Watcher")
            self.btn_toggle_watcher.setObjectName("btnDanger")
            self.lbl_watcher_badge.setText("🟢 Watcher Active")
            self.lbl_watcher_badge.setStyleSheet("color: #34d399; background-color: #0d281e; border: 1px solid #10b981; padding: 5px; border-radius: 6px; font-size: 11px; font-weight: 700;")
            if hasattr(self, 'status_watcher'):
                self.status_watcher.setText("🟢 Watcher: Monitoring")
                self.status_watcher.setStyleSheet("color: #34d399; font-weight: 700; padding: 0 10px;")
            self.statusBar().showMessage("Background Watcher active. Monitoring incoming files.", 3000)
        self.btn_toggle_watcher.setStyle(self.btn_toggle_watcher.style())

    def _add_watch_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Select Folder for Watcher to Monitor")
        if f:
            abs_p = os.path.abspath(f)
            self.list_watched.addItem(abs_p)
            self.watcher.add_watch_path(abs_p)

    def _remove_watch_folder(self):
        row = self.list_watched.currentRow()
        if row >= 0:
            item = self.list_watched.takeItem(row)
            self.watcher.remove_watch_path(item.text())

    def _setup_system_tray(self):
        """Bakes app_icon.ico into Windows System Tray."""
        icon = get_app_icon()
        if icon.isNull():
            return

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Titus OmniSort Pro")

        tray_menu = QMenu()
        act_show = tray_menu.addAction("📂 Open Titus OmniSort Pro")
        act_show.triggered.connect(self._show_and_raise)

        act_float = tray_menu.addAction("📌 Toggle Mini-Target")
        act_float.triggered.connect(self._toggle_floating_widget)

        act_watch = tray_menu.addAction("⚡ Toggle Folder Watcher")
        act_watch.triggered.connect(self._toggle_watcher)

        tray_menu.addSeparator()
        act_exit = tray_menu.addAction("🚪 Exit")
        act_exit.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick or reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_and_raise()

    def _on_watcher_event(self, src: str, dest: str):
        msg = f"Auto-sorted: {os.path.basename(src)} -> {dest}"
        self.list_watcher_log.insertItem(0, msg)
        self.statusBar().showMessage(f"Watcher: {msg}", 4000)
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "Titus OmniSort Pro",
                f"Auto-sorted: {os.path.basename(src)}",
                QSystemTrayIcon.MessageIcon.Information,
                2500
            )

    def _open_dir(self, path: str):
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.information(self, "Folder Not Found", f"Directory does not exist:\n{path}")

    def _open_in_explorer(self):
        target = self.current_source_folder or os.path.expanduser("~")
        self._open_dir(target)

    def _undo_last_batch(self):
        batches = self.undo_manager.get_batches()
        active_batches = [b for b in batches if not b.rolled_back]
        if not active_batches:
            QMessageBox.information(self, "No Batches to Undo", "There are no active sorting sessions available to rollback.")
            return

        last_batch = active_batches[0]
        confirm = QMessageBox.question(
            self,
            "Confirm 1-Click Rollback",
            f"Are you sure you want to rollback batch {last_batch.batch_id}?\n\n"
            f"Description: {last_batch.description}\n"
            f"Files to restore: {len(last_batch.items)}\n"
            f"Date: {last_batch.formatted_time}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            res = self.undo_manager.rollback_batch(last_batch.batch_id)
            if res.get('success'):
                QMessageBox.information(self, "Rollback Successful", f"Successfully restored {res['restored']} files to original paths.")
                self.statusBar().showMessage(f"Rolled back {res['restored']} files.", 5000)
            else:
                QMessageBox.warning(self, "Rollback Warning", f"Issues during rollback:\n" + "\n".join(res.get('errors', [])))
            self._refresh_status_undo()
            if self.current_source_folder:
                self._load_source_folder(self.current_source_folder)

    def _reset_default_rules(self):
        confirm = QMessageBox.question(
            self,
            "Reset Rules",
            "Are you sure you want to restore default automation rules?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.rule_engine._init_default_rules()
            self.rule_engine.save()
            self._refresh_rules_table()
            self.statusBar().showMessage("Restored default rules pipeline.", 3000)

    def _toggle_watcher_state(self, enable: bool):
        if enable and not self.watcher.active:
            self._toggle_watcher()
        elif not enable and self.watcher.active:
            self._toggle_watcher()

    def _refresh_status_undo(self):
        batches = self.undo_manager.get_batches()
        active_count = len([b for b in batches if not b.rolled_back])
        if hasattr(self, 'status_undo_count'):
            self.status_undo_count.setText(f"⏪ Active Sessions: {active_count} ({len(batches)} Total)")

    def _show_about_dialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("About Titus OmniSort Pro")
        dlg.setIconPixmap(get_app_pixmap(64))
        dlg.setText("<h2>Titus OmniSort Pro</h2>")
        dlg.setInformativeText(
            "<b>Version:</b> 2.0 Professional Edition<br>"
            "<b>Architecture:</b> 2-in-1 Folder & File Intelligent Sorter<br><br>"
            "Integrated capabilities inspired by:<br>"
            "• <b>File Juggler</b>: Content inspection (PDF/Word/EXIF), rules pipeline, watcher daemon<br>"
            "• <b>Sortio</b>: 1-click smart presets, rollback undo, duplicate cleaner<br>"
            "• <b>Abelssoft File Organizer</b>: Tactile drop zones & floating desktop widget<br><br>"
            "Developed with Python & PyQt6 for high-performance desktop productivity."
        )
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    def _show_guide_dialog(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Titus OmniSort Pro — Quick Start Guide")
        dlg.setIconPixmap(get_app_pixmap(48))
        dlg.setText("<h3>Quick Start & Feature Workflows</h3>")
        dlg.setInformativeText(
            "<b>1. Folder Auto-Cleaner (Mode 1):</b><br>"
            "Drag any cluttered folder (e.g. Downloads) into the hero banner. "
            "Choose a smart preset (Category, Extension, Year/Month, Size, A-Z), click 'Simulate & Preview', and review before sorting!<br><br>"
            "<b>2. Instant Drop Zones (Mode 2):</b><br>"
            "Drag individual files directly from Windows Explorer onto any bucket tile to route them instantly.<br><br>"
            "<b>3. Floating Mini-Target:</b><br>"
            "Press F8 or click 'Float Target' to toggle an always-on-top desktop drop target.<br><br>"
            "<b>4. Undo & Rollback:</b><br>"
            "Every sort is logged. Press Ctrl+Z or use the History tab to revert any sort operation with 1 click.<br><br>"
            "<b>5. Live Watcher:</b><br>"
            "Press F9 to monitor folders in the background; incoming settled files are auto-sorted via rules."
        )
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        dlg.exec()

    # Drag & drop on main window
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.hero_drop_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a2233;
                    border: 2px dashed #10b981;
                    border-radius: 12px;
                    padding: 18px;
                }
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.hero_drop_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121622, stop:1 #0e121c);
                border: 2px dashed #333f58;
                border-radius: 12px;
                padding: 18px;
            }
            QFrame:hover {
                border-color: #6366f1;
                background-color: #141926;
            }
        """)

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        urls = event.mimeData().urls()
        if not urls:
            return
        first_path = urls[0].toLocalFile()
        if os.path.isdir(first_path):
            self._switch_nav(0)
            self._load_source_folder(first_path)
            event.acceptProposedAction()
        elif os.path.isfile(first_path):
            self._switch_nav(1)
            event.acceptProposedAction()
