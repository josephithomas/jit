"""High-performance 3-tier duplicate file detector and resolver."""
import os
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Callable, Optional, Set, Tuple

from .recycle_bin import send_to_recycle_bin


@dataclass
class DuplicateItem:
    path: str
    size: int
    modified_time: float
    is_original: bool = False


@dataclass
class DuplicateGroup:
    file_hash: str
    size: int
    items: List[DuplicateItem]


class DuplicateFinder:
    """Detects exact duplicate files using size filtering, partial hashing, and full SHA-256."""

    def __init__(self):
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    @staticmethod
    def _get_quick_hash(file_path: str, chunk_size: int = 8192) -> Optional[str]:
        """Hashes the first 8KB of a file for fast screening."""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                chunk = f.read(chunk_size)
                hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return None

    @staticmethod
    def _get_full_hash(file_path: str, chunk_size: int = 65536) -> Optional[str]:
        """Calculates full SHA-256 hash of a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return None

    def scan_directory(
        self, 
        root_dir: str, 
        recursive: bool = True,
        min_size: int = 1,
        progress_cb: Optional[Callable[[int, int, str], None]] = None
    ) -> List[DuplicateGroup]:
        """Scans root_dir and returns grouped duplicate clusters."""
        self._cancel_requested = False
        
        # Phase 1: Collect files and group by size
        size_map: Dict[int, List[str]] = {}
        total_files = 0

        for root, dirs, files in os.walk(root_dir):
            if self._cancel_requested:
                return []
            if not recursive and root != root_dir:
                break
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    sz = os.path.getsize(full_path)
                    if sz >= min_size:
                        size_map.setdefault(sz, []).append(full_path)
                        total_files += 1
                except OSError:
                    continue

        # Phase 2: Quick-hash candidates of same size
        candidates: Dict[str, List[str]] = {}
        processed = 0
        for size, paths in size_map.items():
            if len(paths) < 2:
                continue
            for path in paths:
                if self._cancel_requested:
                    return []
                processed += 1
                if progress_cb and processed % 50 == 0:
                    progress_cb(processed, total_files, path)
                qh = self._get_quick_hash(path)
                if qh:
                    key = f"{size}:{qh}"
                    candidates.setdefault(key, []).append(path)

        # Phase 3: Full hash confirmation
        groups: List[DuplicateGroup] = []
        for key, paths in candidates.items():
            if len(paths) < 2:
                continue
            hash_map: Dict[str, List[str]] = {}
            for path in paths:
                if self._cancel_requested:
                    return []
                fh = self._get_full_hash(path)
                if fh:
                    hash_map.setdefault(fh, []).append(path)

            for file_hash, same_files in hash_map.items():
                if len(same_files) < 2:
                    continue
                items = []
                for i, p in enumerate(same_files):
                    try:
                        st = os.stat(p)
                        items.append(DuplicateItem(
                            path=p,
                            size=st.st_size,
                            modified_time=st.st_mtime,
                            is_original=(i == 0)
                        ))
                    except OSError:
                        continue
                if len(items) >= 2:
                    # Mark oldest as original
                    items.sort(key=lambda x: x.modified_time)
                    for it in items:
                        it.is_original = False
                    items[0].is_original = True
                    groups.append(DuplicateGroup(
                        file_hash=file_hash,
                        size=items[0].size,
                        items=items
                    ))

        return groups
