"""Visual rule builder dialog inspired by File Juggler."""
import os
import time
from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QCheckBox, 
    QScrollArea, QWidget, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from .assets import get_app_icon

from ..core.rule_engine import Rule, Condition, RuleAction


class ConditionRow(QFrame):
    """A single configurable condition in the rule builder."""

    def __init__(self, condition: Optional[Condition] = None, on_delete=None, parent=None):
        super().__init__(parent)
        self.on_delete = on_delete
        self.setStyleSheet("""
            ConditionRow {
                background-color: #1a1d24;
                border: 1px solid #2e3340;
                border-radius: 6px;
            }
        """)
        self._init_ui(condition)

    def _init_ui(self, condition: Optional[Condition]):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # 1. Field
        self.combo_field = QComboBox()
        self.combo_field.addItems([
            "File Name",
            "Extension",
            "Category",
            "File Size (Bytes)",
            "Date Modified (Days Old)",
            "Document Content (PDF/Docx/Txt)",
            "Camera Model (EXIF)"
        ])
        self.combo_field.currentIndexChanged.connect(self._field_changed)
        layout.addWidget(self.combo_field)

        # 2. Operator
        self.combo_op = QComboBox()
        self._populate_operators("File Name")
        layout.addWidget(self.combo_op)

        # 3. Value
        self.txt_val = QLineEdit()
        self.txt_val.setPlaceholderText("Value to match...")
        layout.addWidget(self.txt_val)

        # 4. Remove button
        btn_del = QPushButton("✕")
        btn_del.setFixedSize(26, 26)
        btn_del.setStyleSheet("background-color: #371b1d; color: #f87171; border: none; border-radius: 4px; font-weight: bold;")
        if self.on_delete:
            btn_del.clicked.connect(lambda: self.on_delete(self))
        layout.addWidget(btn_del)

        # Populate from existing condition
        if condition:
            field_map = {
                'filename': 0, 'extension': 1, 'category': 2,
                'size': 3, 'date_modified': 4, 'content': 5, 'camera': 6
            }
            idx = field_map.get(condition.field, 0)
            self.combo_field.setCurrentIndex(idx)
            self._field_changed(idx)

            # Match operator
            op_idx = self.combo_op.findData(condition.operator)
            if op_idx >= 0:
                self.combo_op.setCurrentIndex(op_idx)
            self.txt_val.setText(str(condition.value))

    def _populate_operators(self, field_name: str):
        self.combo_op.clear()
        if "Size" in field_name:
            self.combo_op.addItem("Greater than (>)", "gt")
            self.combo_op.addItem("Less than (<)", "lt")
            self.combo_op.addItem("Equals (=)", "equals")
        elif "Date" in field_name:
            self.combo_op.addItem("Older than (days)", "older_than_days")
            self.combo_op.addItem("Newer than (days)", "newer_than_days")
        else:
            self.combo_op.addItem("contains", "contains")
            self.combo_op.addItem("does not contain", "not_contains")
            self.combo_op.addItem("equals exactly", "equals")
            self.combo_op.addItem("starts with", "starts_with")
            self.combo_op.addItem("ends with", "ends_with")
            self.combo_op.addItem("regex pattern", "regex")
            self.combo_op.addItem("wildcard (*.ext)", "wildcard")

    def _field_changed(self, idx: int):
        field_text = self.combo_field.currentText()
        self._populate_operators(field_text)
        if "Content" in field_text:
            self.txt_val.setPlaceholderText("Keyword inside PDF/Word doc...")
        elif "Size" in field_text:
            self.txt_val.setPlaceholderText("Bytes (e.g. 1048576 for 1MB)")
        elif "Date" in field_text:
            self.txt_val.setPlaceholderText("Number of days (e.g. 30)")
        else:
            self.txt_val.setPlaceholderText("Value to match...")

    def get_condition(self) -> Condition:
        field_name = self.combo_field.currentText()
        field_key = 'filename'
        if "Extension" in field_name:
            field_key = 'extension'
        elif "Category" in field_name:
            field_key = 'category'
        elif "Size" in field_name:
            field_key = 'size'
        elif "Date" in field_name:
            field_key = 'date_modified'
        elif "Content" in field_name:
            field_key = 'content'
        elif "Camera" in field_name:
            field_key = 'camera'

        op = self.combo_op.currentData() or 'contains'
        val = self.txt_val.text().strip()
        return Condition(field=field_key, operator=op, value=val)


class RuleDialog(QDialog):
    """Dialog for creating or editing a File Juggler automation rule."""

    def __init__(self, rule: Optional[Rule] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Juggler Automation Rule Editor")
        self.setWindowIcon(get_app_icon())
        self.resize(650, 520)
        self.existing_rule = rule
        self.condition_rows: List[ConditionRow] = []
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # 1. Rule Name & Status
        top_h = QHBoxLayout()
        top_h.addWidget(QLabel("Rule Name:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Invoices & Receipts Auto-Organizer")
        if self.existing_rule:
            self.txt_name.setText(self.existing_rule.name)
        top_h.addWidget(self.txt_name)

        self.chk_enabled = QCheckBox("Enabled")
        self.chk_enabled.setChecked(self.existing_rule.enabled if self.existing_rule else True)
        top_h.addWidget(self.chk_enabled)
        main_layout.addLayout(top_h)

        # 2. Conditions Header & Mode
        cond_header = QHBoxLayout()
        lbl_if = QLabel("IF:")
        lbl_if.setStyleSheet("font-weight: bold; color: #818cf8; font-size: 14px;")
        cond_header.addWidget(lbl_if)

        self.combo_logic = QComboBox()
        self.combo_logic.addItem("ALL of the following conditions match (AND)", True)
        self.combo_logic.addItem("ANY of the following conditions match (OR)", False)
        if self.existing_rule and not self.existing_rule.match_all:
            self.combo_logic.setCurrentIndex(1)
        cond_header.addWidget(self.combo_logic)

        cond_header.addStretch()

        btn_add_cond = QPushButton("+ Add Condition")
        btn_add_cond.clicked.connect(lambda: self._add_condition_row())
        cond_header.addWidget(btn_add_cond)
        main_layout.addLayout(cond_header)

        # Scroll Area for conditions
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #282c35; border-radius: 6px; }")

        self.cond_container = QWidget()
        self.cond_layout = QVBoxLayout(self.cond_container)
        self.cond_layout.setContentsMargins(8, 8, 8, 8)
        self.cond_layout.setSpacing(6)
        self.cond_layout.addStretch()
        self.scroll_area.setWidget(self.cond_container)
        main_layout.addWidget(self.scroll_area, 1)

        # Populate conditions if editing
        if self.existing_rule and self.existing_rule.conditions:
            for c in self.existing_rule.conditions:
                self._add_condition_row(c)
        else:
            self._add_condition_row()

        # 3. Actions Section
        lbl_then = QLabel("THEN:")
        lbl_then.setStyleSheet("font-weight: bold; color: #34d399; font-size: 14px;")
        main_layout.addWidget(lbl_then)

        action_frame = QFrame()
        action_frame.setStyleSheet("background-color: #17191f; border: 1px solid #292d38; border-radius: 6px; padding: 6px;")
        act_layout = QVBoxLayout(action_frame)
        act_layout.setSpacing(8)

        # Action type
        row_type = QHBoxLayout()
        row_type.addWidget(QLabel("Action:"))
        self.combo_act_type = QComboBox()
        self.combo_act_type.addItem("Move file to target folder", "move")
        self.combo_act_type.addItem("Copy file to target folder", "copy")
        self.combo_act_type.addItem("Send to Recycle Bin", "recycle")
        if self.existing_rule:
            idx = self.combo_act_type.findData(self.existing_rule.action.action_type)
            if idx >= 0:
                self.combo_act_type.setCurrentIndex(idx)
        row_type.addWidget(self.combo_act_type)
        row_type.addStretch()
        act_layout.addLayout(row_type)

        # Target Folder & Tag Insertion
        lbl_dest = QLabel("Destination Folder Template:")
        act_layout.addWidget(lbl_dest)

        dest_h = QHBoxLayout()
        self.txt_dest = QLineEdit()
        self.txt_dest.setPlaceholderText("e.g. Accounting/{year}/{month}")
        if self.existing_rule:
            self.txt_dest.setText(self.existing_rule.action.target_folder)
        dest_h.addWidget(self.txt_dest)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_folder)
        dest_h.addWidget(btn_browse)
        act_layout.addLayout(dest_h)

        # Template Tag Helpers
        tag_h = QHBoxLayout()
        tag_h.addWidget(QLabel("Insert Tag:"))
        for tag in ["{year}", "{month}", "{date}", "{category}", "{ext}", "{name}"]:
            btn_tag = QPushButton(tag)
            btn_tag.setFixedHeight(24)
            btn_tag.setStyleSheet("padding: 2px 6px; font-size: 11px;")
            btn_tag.clicked.connect(lambda _, t=tag: self.txt_dest.insert(t))
            tag_h.addWidget(btn_tag)
        tag_h.addStretch()
        act_layout.addLayout(tag_h)

        main_layout.addWidget(action_frame)

        # 4. Save / Cancel Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Rule")
        btn_save.setObjectName("btnPrimary")
        btn_save.clicked.connect(self._save_rule)
        btn_box.addWidget(btn_save)

        main_layout.addLayout(btn_box)

    def _browse_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Choose Destination Directory")
        if f:
            self.txt_dest.setText(f)

    def _add_condition_row(self, cond: Optional[Condition] = None):
        row = ConditionRow(cond, on_delete=self._remove_condition_row)
        self.condition_rows.append(row)
        # Insert before stretch
        self.cond_layout.insertWidget(self.cond_layout.count() - 1, row)

    def _remove_condition_row(self, row: ConditionRow):
        if len(self.condition_rows) <= 1:
            QMessageBox.information(self, "Notice", "A rule must have at least one condition.")
            return
        self.condition_rows.remove(row)
        row.deleteLater()

    def _save_rule(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please provide a name for this rule.")
            return

        conditions = [r.get_condition() for r in self.condition_rows]
        act_type = self.combo_act_type.currentData()
        target_folder = self.txt_dest.text().strip()

        action = RuleAction(
            action_type=act_type,
            target_folder=target_folder,
            overwrite_mode="rename_new"
        )

        rule_id = self.existing_rule.id if self.existing_rule else f"rule_{int(time.time() * 1000)}"
        self.saved_rule = Rule(
            id=rule_id,
            name=name,
            enabled=self.chk_enabled.isChecked(),
            match_all=self.combo_logic.currentData(),
            conditions=conditions,
            action=action
        )
        self.accept()

