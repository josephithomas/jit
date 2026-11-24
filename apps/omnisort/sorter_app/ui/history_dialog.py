"""History and 1-Click rollback/undo interface inspired by Sortio."""
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt

from ..core.undo_manager import UndoManager


class HistoryUndoWidget(QWidget):
    """View sort operations history and execute 1-click rollback."""

    def __init__(self, undo_manager: UndoManager, parent=None):
        super().__init__(parent)
        self.undo_manager = undo_manager
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        top_h = QHBoxLayout()
        lbl_title = QLabel("Transaction History & 1-Click Rollback")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f3f4f6;")
        top_h.addWidget(lbl_title)

        top_h.addStretch()

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.refresh)
        top_h.addWidget(btn_refresh)

        self.btn_rollback = QPushButton("⏪ Rollback Selected Batch")
        self.btn_rollback.setObjectName("btnDanger")
        self.btn_rollback.clicked.connect(self._rollback_selected)
        top_h.addWidget(self.btn_rollback)

        layout.addLayout(top_h)

        # Splitter: Batch list (top) and File movements details (bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top table: Batches
        self.table_batches = QTableWidget()
        self.table_batches.setColumnCount(5)
        self.table_batches.setHorizontalHeaderLabels(["Batch ID", "Date & Time", "Source Folder", "Items", "Status"])
        self.table_batches.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_batches.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_batches.itemSelectionChanged.connect(self._batch_selected)
        splitter.addWidget(self.table_batches)

        # Bottom table: Operations in batch
        self.table_items = QTableWidget()
        self.table_items.setColumnCount(4)
        self.table_items.setHorizontalHeaderLabels(["Action", "Original Source", "Current Target", "Status"])
        self.table_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        splitter.addWidget(self.table_items)

        splitter.setSizes([200, 260])
        layout.addWidget(splitter, 1)

    def refresh(self):
        batches = self.undo_manager.get_batches()
        self.table_batches.setRowCount(len(batches))

        for row, b in enumerate(batches):
            self.table_batches.setItem(row, 0, QTableWidgetItem(b.batch_id))
            self.table_batches.setItem(row, 1, QTableWidgetItem(b.formatted_time))
            self.table_batches.setItem(row, 2, QTableWidgetItem(b.source_folder))
            self.table_batches.setItem(row, 3, QTableWidgetItem(str(len(b.items))))

            status_str = "Rolled Back" if b.rolled_back else "Active"
            item_status = QTableWidgetItem(status_str)
            if b.rolled_back:
                item_status.setForeground(Qt.GlobalColor.darkGray)
            else:
                item_status.setForeground(Qt.GlobalColor.green)
            self.table_batches.setItem(row, 4, item_status)

        self.table_items.setRowCount(0)

    def _batch_selected(self):
        rows = self.table_batches.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        batch_id = self.table_batches.item(row, 0).text()

        batches = self.undo_manager.get_batches()
        batch = next((b for b in batches if b.batch_id == batch_id), None)
        if not batch:
            return

        self.table_items.setRowCount(len(batch.items))
        for r, item in enumerate(batch.items):
            self.table_items.setItem(r, 0, QTableWidgetItem(item.action.upper()))
            self.table_items.setItem(r, 1, QTableWidgetItem(item.source_path))
            self.table_items.setItem(r, 2, QTableWidgetItem(item.target_path))
            self.table_items.setItem(r, 3, QTableWidgetItem(item.status))

    def _rollback_selected(self):
        rows = self.table_batches.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Select Batch", "Please select a batch from the table to rollback.")
            return

        row = rows[0].row()
        batch_id = self.table_batches.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Rollback",
            f"Are you sure you want to rollback batch {batch_id}?\nAll moved files will be returned to their original folders.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            res = self.undo_manager.rollback_batch(batch_id)
            if res.get('success'):
                QMessageBox.information(self, "Rollback Complete", f"Successfully restored {res['restored']} files.")
            else:
                err_msg = "\n".join(res.get('errors', [])) or res.get('message', 'Failed to rollback.')
                QMessageBox.warning(self, "Rollback Warning", f"Finished with issues:\n{err_msg}")
            self.refresh()

