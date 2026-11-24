"""Persistent undo/rollback manager for file movements and sorting operations."""
import os
import shutil
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from .recycle_bin import send_to_recycle_bin


@dataclass
class FileOperationRecord:
    action: str        # 'move', 'copy', 'rename', 'recycle'
    source_path: str   # Original location
    target_path: str   # New location
    status: str = 'completed'  # 'completed', 'rolled_back', 'failed'


@dataclass
class SortBatchRecord:
    batch_id: str
    timestamp: float
    formatted_time: str
    description: str
    source_folder: str
    items: List[FileOperationRecord]
    rolled_back: bool = False


class UndoManager:
    """Stores history of all operations and rolls back file movements safely."""

    def __init__(self, history_file: Optional[str] = None):
        if not history_file:
            app_dir = os.path.join(os.path.expanduser("~"), ".omnisort_pro")
            os.makedirs(app_dir, exist_ok=True)
            self.history_file = os.path.join(app_dir, "sort_history.json")
        else:
            self.history_file = history_file
        self.batches: List[SortBatchRecord] = []
        self.load()

    def record_batch(self, description: str, source_folder: str, operations: List[FileOperationRecord]) -> str:
        batch_id = f"batch_{int(time.time() * 1000)}"
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
        batch = SortBatchRecord(
            batch_id=batch_id,
            timestamp=time.time(),
            formatted_time=formatted_time,
            description=description,
            source_folder=source_folder,
            items=operations,
            rolled_back=False
        )
        self.batches.insert(0, batch)
        # Keep last 100 batches in history
        self.batches = self.batches[:100]
        self.save()
        return batch_id

    def rollback_batch(self, batch_id: str) -> Dict[str, Any]:
        """Reverses all file operations in the specified batch."""
        batch = next((b for b in self.batches if b.batch_id == batch_id), None)
        if not batch:
            return {'success': False, 'message': 'Batch record not found.'}
        if batch.rolled_back:
            return {'success': False, 'message': 'This batch has already been rolled back.'}

        restored_count = 0
        errors = []
        created_dirs_to_clean = set()

        for op in batch.items:
            try:
                if op.action in ('move', 'rename'):
                    # The file was moved from source_path to target_path
                    if os.path.exists(op.target_path):
                        os.makedirs(os.path.dirname(op.source_path), exist_ok=True)
                        shutil.move(op.target_path, op.source_path)
                        restored_count += 1
                        op.status = 'rolled_back'
                        created_dirs_to_clean.add(os.path.dirname(op.target_path))
                    else:
                        errors.append(f"Target missing: {op.target_path}")
                elif op.action == 'copy':
                    # The file was copied from source_path to target_path
                    if os.path.exists(op.target_path):
                        send_to_recycle_bin(op.target_path)
                        restored_count += 1
                        op.status = 'rolled_back'
                        created_dirs_to_clean.add(os.path.dirname(op.target_path))
            except Exception as e:
                errors.append(f"Failed reversing {os.path.basename(op.target_path)}: {str(e)}")

        # Clean up empty subdirectories created during the sort
        for d in created_dirs_to_clean:
            try:
                if os.path.exists(d) and not os.listdir(d):
                    os.rmdir(d)
            except Exception:
                pass

        batch.rolled_back = True
        self.save()

        return {
            'success': True,
            'restored': restored_count,
            'errors': errors
        }

    def get_batches(self) -> List[SortBatchRecord]:
        return self.batches

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            data = []
            for b in self.batches:
                data.append({
                    'batch_id': b.batch_id,
                    'timestamp': b.timestamp,
                    'formatted_time': b.formatted_time,
                    'description': b.description,
                    'source_folder': b.source_folder,
                    'rolled_back': b.rolled_back,
                    'items': [asdict(op) for op in b.items]
                })
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load(self):
        if not os.path.exists(self.history_file):
            return
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = []
            for item in data:
                items = [FileOperationRecord(**op) for op in item.get('items', [])]
                b = SortBatchRecord(
                    batch_id=item['batch_id'],
                    timestamp=item.get('timestamp', 0.0),
                    formatted_time=item.get('formatted_time', ''),
                    description=item.get('description', ''),
                    source_folder=item.get('source_folder', ''),
                    items=items,
                    rolled_back=item.get('rolled_back', False)
                )
                loaded.append(b)
            self.batches = loaded
        except Exception as e:
            print(f"Error loading history: {e}")

