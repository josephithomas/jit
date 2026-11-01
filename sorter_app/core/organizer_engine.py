"""Core organization engine handling simulation (dry run), preview generation, and execution."""
import os
import shutil
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable

from .classifier import (
    get_file_category, 
    get_date_brackets, 
    get_size_bracket, 
    get_alphabetical_bucket,
    format_file_size
)
from .rule_engine import RuleEngine, Rule
from .undo_manager import UndoManager, FileOperationRecord


@dataclass
class PlannedFileOperation:
    source_path: str
    target_path: str
    action: str            # 'move', 'copy', 'rename', 'recycle'
    category: str
    file_size: int
    rule_or_preset: str
    selected: bool = True
    status: str = "Ready"  # 'Ready', 'Done', 'Skipped', 'Error'
    error_message: str = ""


class OrganizerEngine:
    """Calculates destination paths, resolves naming conflicts, and runs operations."""

    def __init__(self, rule_engine: Optional[RuleEngine] = None, undo_manager: Optional[UndoManager] = None):
        self.rule_engine = rule_engine or RuleEngine()
        self.undo_manager = undo_manager or UndoManager()
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    @staticmethod
    def _resolve_target_conflict(target_path: str, mode: str = "rename_new") -> Optional[str]:
        """Resolves conflict if destination file already exists."""
        if not os.path.exists(target_path):
            return target_path

        if mode == "skip":
            return None
        elif mode == "overwrite":
            return target_path

        # mode == "rename_new"
        folder, filename = os.path.split(target_path)
        name, ext = os.path.splitext(filename)
        counter = 1
        while True:
            candidate = os.path.join(folder, f"{name} ({counter}){ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1

    def generate_preview(
        self,
        file_paths: List[str],
        preset_mode: str,          # 'category', 'extension', 'year_month', 'year', 'date', 'size', 'alphabetical', 'rules', 'direct_target'
        destination_root: Optional[str] = None,
        action: str = 'move',       # 'move' or 'copy'
        conflict_mode: str = 'rename_new',
        direct_target_folder: Optional[str] = None
    ) -> List[PlannedFileOperation]:
        """Simulates sorting without touching files (Dry Run)."""
        planned_ops: List[PlannedFileOperation] = []

        for src in file_paths:
            if not os.path.isfile(src):
                continue

            try:
                stats = os.stat(src)
                sz = stats.st_size
                mtime = stats.st_mtime
            except OSError:
                continue

            filename = os.path.basename(src)
            name_no_ext, ext = os.path.splitext(filename)
            category = get_file_category(filename)
            date_info = get_date_brackets(mtime)
            size_bracket = get_size_bracket(sz)

            # Determine base destination directory
            base_dir = destination_root if destination_root else os.path.dirname(src)
            subfolder = ""
            matched_name = preset_mode
            cur_action = action

            # 1. Direct Target (used by Instant Drop Zones)
            if preset_mode == 'direct_target' and direct_target_folder:
                dest_dir = direct_target_folder

            # 2. Advanced Rule Engine Mode (File Juggler style)
            elif preset_mode == 'rules':
                rule = self.rule_engine.find_matching_rule(src)
                if rule:
                    matched_name = f"Rule: {rule.name}"
                    cur_action = rule.action.action_type
                    # Expand template variables
                    tpl = rule.action.target_folder
                    if tpl:
                        expanded = tpl.format(
                            category=category,
                            ext=ext.lstrip('.').lower(),
                            year=date_info['year'],
                            month=date_info['month'],
                            day=date_info['date'][-2:],
                            date=date_info['date'],
                            size_bracket=size_bracket,
                            name=name_no_ext
                        )
                        dest_dir = os.path.join(base_dir, expanded) if not os.path.isabs(expanded) else expanded
                    else:
                        dest_dir = base_dir
                else:
                    # No rule matched: place in Unsorted
                    matched_name = "No Rule Match (Unsorted)"
                    dest_dir = os.path.join(base_dir, "Unsorted")

            # 3. Sortio-style Smart Presets
            elif preset_mode == 'category':
                dest_dir = os.path.join(base_dir, category)
                matched_name = f"Category: {category}"
            elif preset_mode == 'extension':
                ext_folder = ext.lstrip('.').upper() or 'No Extension'
                dest_dir = os.path.join(base_dir, ext_folder)
                matched_name = f"Extension: {ext_folder}"
            elif preset_mode == 'year_month':
                dest_dir = os.path.join(base_dir, date_info['year_month'])
                matched_name = f"Date: {date_info['year_month']}"
            elif preset_mode == 'year':
                dest_dir = os.path.join(base_dir, date_info['year'])
                matched_name = f"Year: {date_info['year']}"
            elif preset_mode == 'date':
                dest_dir = os.path.join(base_dir, date_info['date'])
                matched_name = f"Day: {date_info['date']}"
            elif preset_mode == 'size':
                dest_dir = os.path.join(base_dir, size_bracket)
                matched_name = f"Size: {size_bracket}"
            elif preset_mode == 'alphabetical':
                alpha_bucket = get_alphabetical_bucket(filename)
                dest_dir = os.path.join(base_dir, alpha_bucket)
                matched_name = f"Alpha: {alpha_bucket}"
            else:
                dest_dir = base_dir

            target_file_path = os.path.join(dest_dir, filename)

            # Skip if file already in final location
            if os.path.abspath(src) == os.path.abspath(target_file_path):
                continue

            # Check conflict
            resolved_target = self._resolve_target_conflict(target_file_path, conflict_mode)
            if not resolved_target:
                # Skipped due to conflict mode
                continue

            planned_ops.append(PlannedFileOperation(
                source_path=src,
                target_path=resolved_target,
                action=cur_action,
                category=category,
                file_size=sz,
                rule_or_preset=matched_name,
                selected=True,
                status="Ready"
            ))

        return planned_ops

    def execute_operations(
        self,
        operations: List[PlannedFileOperation],
        batch_description: str,
        source_root: str,
        progress_cb: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """Executes the approved sorting operations with live callbacks and undo logging."""
        self._cancel_requested = False
        completed_records: List[FileOperationRecord] = []
        errors: List[str] = []
        total = len(operations)
        success_count = 0

        for idx, op in enumerate(operations):
            if self._cancel_requested:
                break

            if not op.selected:
                op.status = "Skipped"
                continue

            if progress_cb:
                progress_cb(idx + 1, total, os.path.basename(op.source_path))

            try:
                target_dir = os.path.dirname(op.target_path)
                os.makedirs(target_dir, exist_ok=True)

                if op.action == 'move':
                    shutil.move(op.source_path, op.target_path)
                    op.status = "Done"
                    completed_records.append(FileOperationRecord(
                        action='move',
                        source_path=op.source_path,
                        target_path=op.target_path
                    ))
                    success_count += 1
                elif op.action == 'copy':
                    shutil.copy2(op.source_path, op.target_path)
                    op.status = "Done"
                    completed_records.append(FileOperationRecord(
                        action='copy',
                        source_path=op.source_path,
                        target_path=op.target_path
                    ))
                    success_count += 1
                else:
                    op.status = "Unknown action"
            except Exception as e:
                op.status = "Error"
                op.error_message = str(e)
                errors.append(f"{os.path.basename(op.source_path)}: {str(e)}")

        batch_id = None
        if completed_records:
            batch_id = self.undo_manager.record_batch(
                description=batch_description,
                source_folder=source_root,
                operations=completed_records
            )

        return {
            'success': len(errors) == 0,
            'completed': success_count,
            'total': total,
            'batch_id': batch_id,
            'errors': errors
        }

