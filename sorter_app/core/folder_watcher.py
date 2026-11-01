"""Real-time background folder watcher with debounce settling time and auto-sorting."""
import os
import time
import threading
from typing import List, Dict, Callable, Optional, Set

from .organizer_engine import OrganizerEngine


class FolderWatcher:
    """Monitors directories for incoming files and automatically triggers organization."""

    def __init__(self, engine: OrganizerEngine, settle_seconds: float = 3.0):
        self.engine = engine
        self.settle_seconds = settle_seconds
        self.watched_paths: List[str] = []
        self.active = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.event_callbacks: List[Callable[[str, str], None]] = []
        # Track pending files: path -> (last_seen_time, last_size)
        self._pending_files: Dict[str, Tuple[float, int]] = {}
        self._known_files: Set[str] = set()

    def add_watch_path(self, path: str):
        abs_p = os.path.abspath(path)
        if os.path.isdir(abs_p) and abs_p not in self.watched_paths:
            self.watched_paths.append(abs_p)

    def remove_watch_path(self, path: str):
        abs_p = os.path.abspath(path)
        if abs_p in self.watched_paths:
            self.watched_paths.remove(abs_p)

    def start(self):
        if self.active:
            return
        self.active = True
        self._stop_event.clear()
        # Seed known files so existing files aren't immediately processed unless desired
        self._known_files.clear()
        for folder in self.watched_paths:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    fp = os.path.join(folder, f)
                    if os.path.isfile(fp):
                        self._known_files.add(fp)

        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.active:
            return
        self.active = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _watch_loop(self):
        while not self._stop_event.is_set():
            now = time.time()
            # 1. Scan watched folders for new files
            for folder in self.watched_paths:
                if not os.path.exists(folder):
                    continue
                try:
                    entries = os.listdir(folder)
                except OSError:
                    continue

                for entry in entries:
                    file_path = os.path.join(folder, entry)
                    if not os.path.isfile(file_path):
                        continue

                    # Ignore partial download files
                    lower_name = entry.lower()
                    if lower_name.endswith(('.crdownload', '.part', '.tmp', '.download')):
                        continue

                    if file_path not in self._known_files and file_path not in self._pending_files:
                        try:
                            sz = os.path.getsize(file_path)
                            self._pending_files[file_path] = (now, sz)
                        except OSError:
                            pass

            # 2. Check pending files for stabilization (settling time)
            ready_to_sort: List[str] = []
            for fp, (first_seen, last_sz) in list(self._pending_files.items()):
                if not os.path.exists(fp):
                    del self._pending_files[fp]
                    continue

                try:
                    current_sz = os.path.getsize(fp)
                except OSError:
                    continue

                # If size changed, reset timer
                if current_sz != last_sz:
                    self._pending_files[fp] = (now, current_sz)
                elif (now - first_seen) >= self.settle_seconds:
                    ready_to_sort.append(fp)
                    del self._pending_files[fp]
                    self._known_files.add(fp)

            # 3. Process stabilized files
            if ready_to_sort:
                ops = self.engine.generate_preview(
                    file_paths=ready_to_sort,
                    preset_mode='rules'
                )
                if ops:
                    res = self.engine.execute_operations(
                        operations=ops,
                        batch_description="Auto-Watcher Live Sort",
                        source_root="Watched Folders"
                    )
                    for op in ops:
                        if op.status == "Done":
                            for cb in self.event_callbacks:
                                cb(op.source_path, op.target_path)

            time.sleep(1.0)

