"""Real-time background folder watcher with debounce settling time and auto-sorting."""
import os
import time
import threading
from typing import List, Dict, Callable, Optional, Set, Tuple

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

    def add_event_callback(self, cb: Callable[[str, str], None]):
        self.event_callbacks.append(cb)

    def start(self):
        if self.active:
            return
        self.active = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.active = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _scan_once(self):
        now = time.time()
        current_files: Set[str] = set()

        for watch_path in list(self.watched_paths):
            if not os.path.isdir(watch_path):
                continue
            try:
                for name in os.listdir(watch_path):
                    full = os.path.join(watch_path, name)
                    if not os.path.isfile(full):
                        continue
                    current_files.add(full)
                    try:
                        size = os.path.getsize(full)
                    except OSError:
                        continue

                    if full not in self._known_files:
                        # New file appeared
                        self._pending_files[full] = (now, size)
                    elif full in self._pending_files:
                        last_time, last_size = self._pending_files[full]
                        if size != last_size:
                            # Still growing
                            self._pending_files[full] = (now, size)
            except OSError:
                continue

        # Promote settled files
        ready = []
        for path, (seen_at, size) in list(self._pending_files.items()):
            if path not in current_files:
                self._pending_files.pop(path, None)
                continue
            if now - seen_at >= self.settle_seconds:
                ready.append(path)

        for path in ready:
            self._pending_files.pop(path, None)
            self._known_files.add(path)
            try:
                self.engine.organize_file(path)
                for cb in self.event_callbacks:
                    try:
                        cb("organized", path)
                    except Exception:
                        pass
            except Exception as e:
                for cb in self.event_callbacks:
                    try:
                        cb("error", f"{path}: {e}")
                    except Exception:
                        pass

        # Drop known files that disappeared
        self._known_files &= current_files

    def _watch_loop(self):
        while not self._stop_event.is_set():
            try:
                self._scan_once()
            except Exception:
                pass
            self._stop_event.wait(1.0)
