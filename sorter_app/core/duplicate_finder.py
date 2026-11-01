"""High-performance 3-tier duplicate file detector and resolver."""
import os
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Callable, Optional, Set

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

        # Keep only sizes with 2+ files
        potential_candidates: List[str] = []
        for sz, files in size_map.items():
            if len(files) > 1:
                potential_candidates.extend(files)

        if not potential_candidates:
            return []

        # Phase 2: Quick partial hash comparison
        quick_hash_map: Dict[Tuple[int, str], List[str]] = {}
        processed = 0
        total_candidates = len(potential_candidates)

        for p in potential_candidates:
            if self._cancel_requested:
                return []
            processed += 1
            if progress_cb and processed % 20 == 0:
                progress_cb(processed, total_candidates, f"Quick checking {os.path.basename(p)}")

            try:
                sz = os.path.getsize(p)
                qhash = self._get_quick_hash(p)
                if qhash:
                    quick_hash_map.setdefault((sz, qhash), []).append(p)
            except OSError:
                continue

        # Phase 3: Full SHA-256 for exact matches
        final_groups: List[DuplicateGroup] = []
        full_hash_candidates: List[str] = []

        for (sz, _), files in quick_hash_map.items():
            if len(files) > 1:
                full_hash_candidates.extend(files)

        full_hash_map: Dict[str, List[str]] = {}
        processed = 0
        total_full = len(full_hash_candidates)

        for p in full_hash_candidates:
            if self._cancel_requested:
                return []
            processed += 1
            if progress_cb:
                progress_cb(processed, total_full, f"Computing SHA-256 for {os.path.basename(p)}")

            fhash = self._get_full_hash(p)
            if fhash:
                full_hash_map.setdefault(fhash, []).append(p)

        for fhash, files in full_hash_map.items():
            if len(files) > 1:
                try:
                    file_size = os.path.getsize(files[0])
                except OSError:
                    file_size = 0

                items = []
                # Sort by modification time ascending so oldest is first
                files_with_mtime = []
                for f in files:
                    try:
                        mtime = os.path.getmtime(f)
                    except OSError:
                        mtime = 0
                    files_with_mtime.append((f, mtime))
                
                files_with_mtime.sort(key=lambda x: x[1])

                for idx, (f_path, mtime) in enumerate(files_with_mtime):
                    items.append(DuplicateItem(
                        path=f_path,
                        size=file_size,
                        modified_time=mtime,
                        is_original=(idx == 0) # Default: oldest is original
                    ))

                final_groups.append(DuplicateGroup(
                    file_hash=fhash,
                    size=file_size,
                    items=items
                ))

        return final_groups

    @staticmethod
    def resolve_duplicates(paths_to_remove: List[str], use_recycle_bin: bool = True) -> int:
        """Removes duplicate files safely."""
        if not paths_to_remove:
            return 0
        if use_recycle_bin:
            send_to_recycle_bin(paths_to_remove)
            return len(paths_to_remove)
        else:
            removed = 0
            for p in paths_to_remove:
                try:
                    os.remove(p)
                    removed += 1
                except OSError:
                    pass
            return removed

