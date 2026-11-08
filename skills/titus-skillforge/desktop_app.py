"""
Titus SkillForge Studio - Native Windows Desktop Application.
Features:
- Native Windows Menu Bar (File, Edit, Tools, View, Help)
- Native Action Toolbar with Icons & Shortcuts
- Embedded WebEngine View running local FastAPI backend
- Socket Polling & Health Guard (eliminates 127.0.0.1 connection refused)
- Titus Logo baked into Taskbar, Window Title, About Dialog & Status Bar
"""

from __future__ import annotations
import sys
import os
import time
import socket
import threading
import webbrowser
import traceback
import io
from pathlib import Path

# Windowed EXEs (pythonw / --windowed) have no console
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Support both normal Python run and PyInstaller frozen EXE
if getattr(sys, "frozen", False):
    # Running as compiled EXE
    APP_DIR = Path(sys._MEIPASS)          # type: ignore[attr-defined]
    # Keep user-writable data next to the EXE
    USER_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent
    USER_DIR = APP_DIR

ASSETS_DIR = APP_DIR / "assets"
STATIC_DIR = APP_DIR / "static"
LOGO_PATH = ASSETS_DIR / "titus-logo.png"
ICO_PATH = ASSETS_DIR / "icon.ico"

# Ensure assets directory exists (only when not frozen)
if not getattr(sys, "frozen", False):
    ASSETS_DIR.mkdir(exist_ok=True)

# Logging must be available before any function that may call it
LOG_FILE = USER_DIR / "app_debug.log"

def log_debug(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

# Add APP_DIR to python path for internal imports
sys.path.insert(0, str(APP_DIR))

import uvicorn
from app import app as fastapi_app
from parser import DocumentParser
from synthesizer import SkillSynthesizer
from validator import SkillValidator
from installer import SkillInstaller


def free_port(port: int = 8000):
    """Ensure standard port 8000 is freed from any stale processes."""
    try:
        import subprocess
        res = subprocess.run("netstat -ano", shell=True, capture_output=True, text=True, timeout=8)
        my_pid = os.getpid()
        for line in res.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    try:
                        pid = int(parts[-1])
                    except ValueError:
                        continue
                    if pid != my_pid and pid > 4:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True, timeout=5)
                        time.sleep(0.4)
    except Exception as e:
        log_debug(f"Warning freeing port {port}: {e}")


def wait_for_server(host: str, port: int, timeout: float = 12.0) -> bool:
    """Poll socket until backend server accepts connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.15)
    return False


class ServerThread(threading.Thread):
    """Background thread running Uvicorn server."""
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        try:
            # Windowed EXEs have no console — stdout/stderr are None.
            # Uvicorn's default formatter calls sys.stdout.isatty() and crashes.
            import io
            if sys.stdout is None:
                sys.stdout = io.StringIO()
            if sys.stderr is None:
                sys.stderr = io.StringIO()

            config = uvicorn.Config(
                app=fastapi_app,
                host=self.host,
                port=self.port,
                log_level="warning",
                access_log=False,
                log_config=None,  # avoid uvicorn's color/isatty formatter
            )
            self.server = uvicorn.Server(config)
            self.server.run()
        except Exception as e:
            log_debug(f"Error in ServerThread: {e}\n{traceback.format_exc()}")

    def stop(self):
        if self.server:
            self.server.should_exit = True


# PyQt6 GUI Application
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QStatusBar, QToolBar, QLabel,
    QProgressBar, QDialog, QTextEdit, QPushButton, QTabWidget
)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont, QKeySequence

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False


class AboutDialog(QDialog):
    """Bespoke About dialog featuring Titus Logo and system spec."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Titus SkillForge Studio")
        self.setFixedSize(540, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Logo display
        if LOGO_PATH.exists():
            logo_label = QLabel()
            pix = QPixmap(str(LOGO_PATH))
            if not pix.isNull():
                scaled = pix.scaled(180, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)

        title = QLabel("Titus SkillForge Studio")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0f172a;")
        layout.addWidget(title)

        subtitle = QLabel("Universal SKILL.md Creator & Cross-Platform Orchestrator\nVersion 1.0.0 (Production Release)")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; font-size: 13px; line-height: 1.4;")
        layout.addWidget(subtitle)

        info_box = QTextEdit()
        info_box.setReadOnly(True)
        info_box.setHtml("""
        <div style="font-family: Segoe UI, sans-serif; font-size: 12px; color: #334155; line-height: 1.6;">
            <p><b>Multi-Format Ingestion:</b> PDF, DOCX, PPTX, Images (OCR), Markdown, Plain Text.</p>
            <p><b>Cross-Platform Synthesis:</b> Generates standard <code>SKILL.md</code> files strictly compliant with:</p>
            <ul>
                <li><b>Anthropic Claude</b> (Skill specification & system boundaries)</li>
                <li><b>xAI Grok</b> (Reasoning modes & skill tools)</li>
                <li><b>OpenAI ChatGPT</b> (Custom GPT Actions & system skills)</li>
                <li><b>Google Gemini & Antigravity</b> (Native Agent Skill directory standards)</li>
            </ul>
            <p><b>Safety & Guardrails:</b> Automatic boundary isolation, risk level categorization, and JSON/YAML validation.</p>
            <p><b>Author:</b> Dr. Joseph I Thomas | Titus Universal Suite</p>
            <p><b>Repository Anchor:</b> <a href="https://github.com/josephithomas/jit">github.com/josephithomas/jit</a></p>
        </div>
        """)
        layout.addWidget(info_box)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #0284c7;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #0369a1;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class MainWindow(QMainWindow):
    def __init__(self, port: int):
        super().__init__()
        self.port = port
        self.server_url = f"http://127.0.0.1:{self.port}"
        self.current_file_path = None

        self.setWindowTitle("Titus SkillForge Studio — Universal SKILL.md Creator")
        self.setMinimumSize(1180, 800)
        self.resize(1366, 880)

        # Set Window Icons
        if ICO_PATH.exists():
            self.setWindowIcon(QIcon(str(ICO_PATH)))
        elif LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))

        # Setup Menu Bar, Tool Bar, Status Bar
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()

        # Central View
        self.setup_central_view()

    def setup_menubar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_act = QAction("&New Skill", self)
        new_act.setShortcut(QKeySequence.StandardKey.New)
        new_act.triggered.connect(self.on_new_skill)
        file_menu.addAction(new_act)

        open_act = QAction("&Open Document / Image / PDF...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.on_open_file)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        save_act = QAction("&Save SKILL.md As...", self)
        save_act.setShortcut(QKeySequence.StandardKey.Save)
        save_act.triggered.connect(self.on_save_skill)
        file_menu.addAction(save_act)

        export_zip_act = QAction("Export &ZIP Skill Package...", self)
        export_zip_act.setShortcut("Ctrl+E")
        export_zip_act.triggered.connect(self.on_export_zip)
        file_menu.addAction(export_zip_act)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence.StandardKey.Quit)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        copy_act = QAction("&Copy SKILL.md to Clipboard", self)
        copy_act.setShortcut(QKeySequence.StandardKey.Copy)
        copy_act.triggered.connect(self.on_copy_skill)
        edit_menu.addAction(copy_act)

        clear_act = QAction("Clear All", self)
        clear_act.setShortcut("Ctrl+L")
        clear_act.triggered.connect(self.on_clear_all)
        edit_menu.addAction(clear_act)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        synth_act = QAction("⚡ &Synthesize SKILL.md", self)
        synth_act.setShortcut("F5")
        synth_act.triggered.connect(self.on_trigger_synthesize)
        tools_menu.addAction(synth_act)

        val_act = QAction("🛡️ &Validate AI Compatibility", self)
        val_act.setShortcut("F6")
        val_act.triggered.connect(self.on_trigger_validate)
        tools_menu.addAction(val_act)

        tools_menu.addSeparator()

        install_anti_act = QAction("🚀 Install to Antigravity / Gemini", self)
        install_anti_act.triggered.connect(lambda: self.on_install_direct("antigravity"))
        tools_menu.addAction(install_anti_act)

        install_claude_act = QAction("🚀 Install to Claude Desktop", self)
        install_claude_act.triggered.connect(lambda: self.on_install_direct("claude"))
        tools_menu.addAction(install_claude_act)

        install_ws_act = QAction("📁 Install to Workspace Folder...", self)
        install_ws_act.triggered.connect(self.on_install_to_workspace)
        tools_menu.addAction(install_ws_act)

        # View Menu
        view_menu = menubar.addMenu("&View")

        reload_act = QAction("&Reload Interface", self)
        reload_act.setShortcut(QKeySequence.StandardKey.Refresh)
        reload_act.triggered.connect(self.on_reload_page)
        view_menu.addAction(reload_act)

        browser_act = QAction("🌐 Open in System &Browser", self)
        browser_act.setShortcut("Ctrl+B")
        browser_act.triggered.connect(self.on_open_in_browser)
        view_menu.addAction(browser_act)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        guide_act = QAction("SKILL.md &Standards & Guide", self)
        guide_act.triggered.connect(self.on_show_guide)
        help_menu.addAction(guide_act)

        compat_act = QAction("Cross-Platform &Compatibility Matrix", self)
        compat_act.triggered.connect(self.on_show_compat_matrix)
        help_menu.addAction(compat_act)

        help_menu.addSeparator()

        about_act = QAction("&About Titus SkillForge Studio", self)
        about_act.triggered.connect(self.on_about)
        help_menu.addAction(about_act)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Actions")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                padding: 4px 8px;
                spacing: 8px;
            }
            QToolButton {
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                padding: 6px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background: #ffffff;
                color: #334155;
            }
            QToolButton:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
            }
        """)

        # Brand Indicator in Toolbar
        if LOGO_PATH.exists():
            brand_label = QLabel()
            pix = QPixmap(str(LOGO_PATH))
            if not pix.isNull():
                scaled = pix.scaled(110, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                brand_label.setPixmap(scaled)
                brand_label.setContentsMargins(4, 0, 12, 0)
                toolbar.addWidget(brand_label)

        open_btn = QAction("📄 Open File", self)
        open_btn.setToolTip("Upload text, PDF, Word doc, PowerPoint, or Image (OCR)")
        open_btn.triggered.connect(self.on_open_file)
        toolbar.addAction(open_btn)

        toolbar.addSeparator()

        synth_btn = QAction("⚡ Synthesize SKILL.md", self)
        synth_btn.setToolTip("Synthesize document into standardized SKILL.md (F5)")
        synth_btn.triggered.connect(self.on_trigger_synthesize)
        toolbar.addAction(synth_btn)

        val_btn = QAction("🛡️ Validate All", self)
        val_btn.setToolTip("Lint and test for Claude, Grok, ChatGPT, Gemini & Antigravity (F6)")
        val_btn.triggered.connect(self.on_trigger_validate)
        toolbar.addAction(val_btn)

        toolbar.addSeparator()

        zip_btn = QAction("📦 Export ZIP", self)
        zip_btn.setToolTip("Export ready-to-distribute .zip skill package")
        zip_btn.triggered.connect(self.on_export_zip)
        toolbar.addAction(zip_btn)

        save_btn = QAction("💾 Save SKILL.md", self)
        save_btn.setToolTip("Save raw SKILL.md file to local disk")
        save_btn.triggered.connect(self.on_save_skill)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        browser_btn = QAction("🌐 Open in Browser", self)
        browser_btn.setToolTip("Launch in your default browser (Chrome/Edge/Firefox)")
        browser_btn.triggered.connect(self.on_open_in_browser)
        toolbar.addAction(browser_btn)

        self.addToolBar(toolbar)

    def setup_statusbar(self):
        status = QStatusBar()
        status.setStyleSheet("""
            QStatusBar {
                background: #0f172a;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                padding: 4px;
            }
        """)

        self.status_label = QLabel("Ready | Titus SkillForge Universal v1.0.0")
        self.status_label.setStyleSheet("color: #38bdf8; font-weight: 500;")
        status.addWidget(self.status_label, 1)

        self.port_label = QLabel(f"Server: 127.0.0.1:{self.port} (Active)")
        self.port_label.setStyleSheet("color: #4ade80; margin-right: 12px;")
        status.addPermanentWidget(self.port_label)

        self.setStatusBar(status)

    def setup_central_view(self):
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            self.web_view.setUrl(QUrl(self.server_url))
            self.setCentralWidget(self.web_view)
        else:
            # Fallback widget if WebEngine is not available
            fallback = QWidget()
            layout = QVBoxLayout(fallback)
            info = QLabel(f"Titus SkillForge Backend is active on: {self.server_url}\nClick below to open in your browser.")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn = QPushButton("Open Titus SkillForge in Browser")
            btn.clicked.connect(self.on_open_in_browser)
            layout.addWidget(info)
            layout.addWidget(btn)
            self.setCentralWidget(fallback)

    def on_new_skill(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.resetForm();")
        self.status_label.setText("New skill started.")

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document, Image, or Specification File",
            "",
            "All Supported (*.txt *.md *.pdf *.docx *.pptx *.png *.jpg *.jpeg *.webp *.json *.yaml);;PDF Documents (*.pdf);;Word Documents (*.docx);;Images (*.png *.jpg *.jpeg *.webp);;Markdown (*.md);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            p = Path(file_path)
            content_bytes = p.read_bytes()
            parsed = DocumentParser.parse_file(content_bytes, p.name)
            extracted_text = parsed.get("text", "")

            # Inject extracted text and file name into the webview via JavaScript
            js_script = f"""
            (function() {{
                const inputArea = document.getElementById('rawTextInput');
                if (inputArea) {{
                    inputArea.value = {repr(extracted_text)};
                    inputArea.dispatchEvent(new Event('input'));
                }}
                const nameInput = document.getElementById('skillNameInput');
                if (nameInput && !nameInput.value) {{
                    nameInput.value = {repr(p.stem.lower().replace(' ', '-'))};
                }}
                const fileInfo = document.getElementById('fileUploadBadge');
                if (fileInfo) {{
                    fileInfo.textContent = 'Loaded: ' + {repr(p.name)};
                    fileInfo.style.display = 'inline-block';
                }}
            }})();
            """
            if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
                self.web_view.page().runJavaScript(js_script)

            self.status_label.setText(f"Loaded: {p.name} ({len(extracted_text)} characters extracted)")
            QMessageBox.information(self, "File Ingested", f"Successfully extracted text from:\n{p.name}\n\nCharacters: {len(extracted_text)}\nFormat: {parsed.get('format')}")
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"Could not parse file:\n{str(e)}")

    def on_trigger_synthesize(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.synthesizeSkill();")
        self.status_label.setText("Synthesizing SKILL.md...")

    def on_trigger_validate(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.validateCurrent();")
        self.status_label.setText("Validating cross-platform compatibility...")

    def on_save_skill(self):
        if not WEBENGINE_AVAILABLE or not hasattr(self, 'web_view'):
            return

        # Fetch current markdown from webview and prompt user for save location
        def callback(content):
            if not content or not content.strip():
                QMessageBox.warning(self, "Empty Skill", "There is no generated SKILL.md content to save.")
                return

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Standard SKILL.md",
                "SKILL.md",
                "Markdown (*.md);;All Files (*.*)"
            )
            if save_path:
                try:
                    Path(save_path).write_text(content, encoding="utf-8")
                    self.status_label.setText(f"Saved: {save_path}")
                    QMessageBox.information(self, "Saved", f"Skill successfully saved to:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{str(e)}")

        self.web_view.page().runJavaScript("document.getElementById('skillMarkdownOutput') ? document.getElementById('skillMarkdownOutput').value : ''", callback)

    def on_export_zip(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.exportZip();")
        self.status_label.setText("Exporting ZIP package...")

    def on_copy_skill(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.copyToClipboard();")
        self.status_label.setText("Copied SKILL.md to clipboard.")

    def on_clear_all(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("if (window.SkillForgeApp) window.SkillForgeApp.clearAll();")
        self.status_label.setText("Cleared workspace.")

    def on_install_direct(self, target: str):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript(f"if (window.SkillForgeApp) window.SkillForgeApp.installSkill('{target}');")
        self.status_label.setText(f"Installing skill to {target}...")

    def on_install_to_workspace(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Workspace Root Directory")
        if not folder:
            return

        def callback(content):
            if not content or not content.strip():
                QMessageBox.warning(self, "Empty Skill", "Please synthesize a skill first before installing.")
                return

            try:
                name = "custom-skill"
                result = SkillInstaller.install_to_workspace(name, content, folder)
                if result.get("success"):
                    QMessageBox.information(self, "Installed", f"Skill installed to workspace:\n{result.get('path')}")
                else:
                    QMessageBox.warning(self, "Installation Note", result.get("message", "Could not install"))
            except Exception as e:
                QMessageBox.critical(self, "Install Error", str(e))

        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.page().runJavaScript("document.getElementById('skillMarkdownOutput') ? document.getElementById('skillMarkdownOutput').value : ''", callback)

    def on_reload_page(self):
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view'):
            self.web_view.reload()
            self.status_label.setText("Reloaded interface.")

    def on_open_in_browser(self):
        webbrowser.open(self.server_url)
        self.status_label.setText(f"Opened {self.server_url} in browser.")

    def on_show_guide(self):
        QMessageBox.information(
            self,
            "SKILL.md Standards & Guidelines",
            "A valid SKILL.md consists of:\n\n"
            "1. YAML Frontmatter (--- ... ---)\n"
            "   - name: lower-case-with-hyphens (max 48 chars)\n"
            "   - description: 1-2 sentence overview of what the skill does\n"
            "   - tags / category / version / author\n\n"
            "2. Structured Markdown Body:\n"
            "   - ## Purpose & Overview\n"
            "   - ## Operating Boundaries & Safety\n"
            "   - ## Procedural Workflow (numbered steps)\n"
            "   - ## Input / Output Contracts & Schemas\n"
            "   - ## Concrete Implementation Examples\n\n"
            "Compatible across Claude, Grok, ChatGPT, Gemini, and Antigravity."
        )

    def on_show_compat_matrix(self):
        QMessageBox.information(
            self,
            "Cross-Platform Compatibility Matrix",
            "Titus SkillForge generates SKILL.md files tested against:\n\n"
            "• Anthropic Claude: Fully compliant (YAML name, description, constraints)\n"
            "• xAI Grok: Compatible (tool definitions, structured reasoning steps)\n"
            "• OpenAI ChatGPT: Supported (Custom GPT Instructions & Action schemas)\n"
            "• Google Gemini & Antigravity: Native standard (~/.gemini/config/skills/<name>/SKILL.md)\n"
            "• Local Workspaces: Standalone package with README and test harness."
        )

    def on_about(self):
        dlg = AboutDialog(self)
        dlg.exec()


def main():
    log_debug("Starting Titus SkillForge Studio...")
    try:
        port = 8000
        # 1. Clear any stale process on port 8000
        free_port(port)
        log_debug(f"Target port: {port}")

        # 2. Start FastAPI server thread bound to 0.0.0.0
        server_thread = ServerThread("0.0.0.0", port)
        server_thread.start()
        log_debug("Server thread started on 0.0.0.0:8000.")

        # 3. Wait until server responds to socket connections
        server_ready = wait_for_server("127.0.0.1", port, timeout=12.0)
        log_debug(f"Server ready status: {server_ready}")

        # 4. Initialize PyQt6 GUI only (no system browser — native window is the UI)
        app = QApplication(sys.argv)
        app.setApplicationName("Titus SkillForge Studio")
        app.setOrganizationName("Titus Universal")
        # Bake Titus icon at application level (taskbar, Alt-Tab, etc.)
        if ICO_PATH.exists():
            app.setWindowIcon(QIcon(str(ICO_PATH)))
        elif LOGO_PATH.exists():
            app.setWindowIcon(QIcon(str(LOGO_PATH)))

        window = MainWindow(port=port)
        window.show()
        window.raise_()
        window.activateWindow()
        log_debug("Native window displayed, entering event loop...")

        # Run application event loop
        exit_code = app.exec()
        log_debug(f"Application exited with code: {exit_code}")

        # Stop server gracefully on window exit
        server_thread.stop()
        sys.exit(exit_code)
    except Exception as e:
        log_debug(f"FATAL EXCEPTION in main: {e}\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_debug(f"Unhandled top-level exception: {e}\n{traceback.format_exc()}")

