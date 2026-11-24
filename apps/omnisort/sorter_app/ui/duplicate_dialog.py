"""Duplicate file scanner and cleaner interface inspired by Sortio."""
import os
import time
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, 
    QCheckBox, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..core.duplicate_finder import DuplicateFinder, DuplicateGroup
from ..core.classifier import format_file_size


class DuplicateScanWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished_scan = pyqtSignal(list)

    def __init__(self, root_dir: str, recursive: bool = True, parent=None):
        super().__init__(parent)
        self.root_dir = root_dir
        self.recursive = recursive
        self.finder = DuplicateFinder()

    def run(self):
        groups = self.finder.scan_directory(
            root_dir=self.root_dir,
            recursive=self.recursive,
            progress_cb=lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
        )
        self.finished_scan.emit(groups)

    def cancel(self):
        self.finder.cancel()


class DuplicateCleanerWidget(QWidget):
    """Sortio-style duplicate file detector with one-click cleanup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups: List[DuplicateGroup] = []
        self._worker: Optional[DuplicateScanWorker] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header controls
        top_h = QHBoxLayout()
        top_h.addWidget(QLabel("Folder to Scan:"))

        self.txt_folder = QLabel("No folder selected")
        self.txt_folder.setStyleSheet("background-color: #1e222a; padding: 6px 12px; border-radius: 6px; color: #93c5fd;")
        top_h.addWidget(self.txt_folder, 1)

        btn_browse = QPushButton("📁 Browse...")
        btn_browse.clicked.connect(self._browse_folder)
        top_h.addWidget(btn_browse)

        self.chk_recursive = QCheckBox("Scan Subfolders")
        self.chk_recursive.setChecked(True)
        top_h.addWidget(self.chk_recursive)

        self.btn_scan = QPushButton("🔍 Find Duplicates")
        self.btn_scan.setObjectName("btnPrimary")
        self.btn_scan.clicked.connect(self._start_scan)
        top_h.addWidget(self.btn_scan)

        layout.addLayout(top_h)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Select a folder and click 'Find Duplicates' to discover identical files.")
        self.lbl_status.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.lbl_status)

        # Tree Widget for duplicate groups
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File Name / Path", "Size", "Modified Date", "Action"])
        self.tree.setColumnWidth(0, 420)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 160)
        layout.addWidget(self.tree, 1)

        # Bottom Selection and Resolution Toolbar
        bottom_h = QHBoxLayout()
        lbl_select = QLabel("Quick Select:")
        lbl_select.setStyleSheet("font-weight: bold;")
        bottom_h.addWidget(lbl_select)

        btn_sel_oldest = QPushButton("Keep Oldest (Select Newer)")
        btn_sel_oldest.clicked.connect(lambda: self._select_all_duplicates(keep='oldest'))
        bottom_h.addWidget(btn_sel_oldest)

        btn_sel_newest = QPushButton("Keep Newest (Select Older)")
        btn_sel_newest.clicked.connect(lambda: self._select_all_duplicates(keep='newest'))
        bottom_h.addWidget(btn_sel_newest)

        btn_clear = QPushButton("Deselect All")
        btn_clear.clicked.connect(self._deselect_all)
        bottom_h.addWidget(btn_clear)

        bottom_h.addStretch()

        self.btn_recycle = QPushButton("🗑️ Recycle Selected Duplicates")
        self.btn_recycle.setObjectName("btnDanger")
        self.btn_recycle.clicked.connect(self._recycle_selected)
        bottom_h.addWidget(self.btn_recycle)

        layout.addLayout(bottom_h)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Scan for Duplicates")
        if folder:
            self.txt_folder.setText(os.path.abspath(folder))

    def _start_scan(self):
        folder = self.txt_folder.text()
        if not os.path.isdir(folder):
            QMessageBox.warning(self, "Invalid Folder", "Please choose a valid folder to scan.")
            return

        self.tree.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_scan.setEnabled(False)

        self._worker = DuplicateScanWorker(folder, recursive=self.chk_recursive.isChecked())
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_scan.connect(self._on_scan_finished)
        self._worker.start()

    def _on_progress(self, cur: int, total: int, msg: str):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(cur)
        self.lbl_status.setText(msg)

    def _on_scan_finished(self, groups: List[DuplicateGroup]):
        self.groups = groups
        self.btn_scan.setEnabled(True)
        self.progress_bar.setVisible(False)

        if not groups:
            self.lbl_status.setText("✅ No duplicate files found in this directory.")
            return

        total_dups = sum(len(g.items) - 1 for g in groups)
        wasted_bytes = sum(g.size * (len(g.items) - 1) for g in groups)
        self.lbl_status.setText(f"Found {total_dups} duplicate files wasting {format_file_size(wasted_bytes)} across {len(groups)} groups.")

        # Populate tree
        for grp in groups:
            root_item = QTreeWidgetItem(self.tree)
            root_item.setText(0, f"Duplicate Cluster (SHA-256: {grp.file_hash[:12]}...)")
            root_item.setText(1, format_file_size(grp.size))
            root_item.setExpanded(True)

            for idx, item in enumerate(grp.items):
                child = QTreeWidgetItem(root_item)
                child.setText(0, item.path)
                child.setText(1, format_file_size(item.size))
                mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.modified_time))
                child.setText(2, mtime_str)

                # Checkbox
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if idx == 0:
                    child.setText(3, "Original (Kept)")
                    child.setCheckState(0, Qt.CheckState.Unchecked)
                else:
                    child.setText(3, "Duplicate")
                    child.setCheckState(0, Qt.CheckState.Checked)

    def _select_all_duplicates(self, keep: str = 'oldest'):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            count = group_item.childCount()
            for j in range(count):
                child = group_item.child(j)
                if keep == 'oldest':
                    # Keep index 0, check others
                    child.setCheckState(0, Qt.CheckState.Unchecked if j == 0 else Qt.CheckState.Checked)
                elif keep == 'newest':
                    # Keep last index, check others
                    child.setCheckState(0, Qt.CheckState.Unchecked if j == count - 1 else Qt.CheckState.Checked)

    def _deselect_all(self):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            for j in range(group_item.childCount()):
                group_item.child(j).setCheckState(0, Qt.CheckState.Unchecked)

    def _recycle_selected(self):
        selected_paths: List[str] = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            group_item = root.child(i)
            for j in range(group_item.childCount()):
                child = group_item.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    selected_paths.append(child.text(0))

        if not selected_paths:
            QMessageBox.information(self, "Nothing Selected", "Please select at least one duplicate file to recycle.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Safe Recycle",
            f"Are you sure you want to move {len(selected_paths)} duplicate files to the Windows Recycle Bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            removed = DuplicateFinder.resolve_duplicates(selected_paths, use_recycle_bin=True)
            QMessageBox.information(self, "Success", f"Safely recycled {removed} duplicate files.")
            self._start_scan()

