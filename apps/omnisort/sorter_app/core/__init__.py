"""Core sorter modules package."""
from .classifier import CATEGORY_MAP, CATEGORY_ICONS, get_file_category, get_date_brackets, get_size_bracket, format_file_size
from .content_inspector import ContentInspector
from .rule_engine import RuleEngine, Rule, Condition, RuleAction
from .undo_manager import UndoManager, FileOperationRecord, SortBatchRecord
from .duplicate_finder import DuplicateFinder, DuplicateGroup, DuplicateItem
from .organizer_engine import OrganizerEngine, PlannedFileOperation
from .folder_watcher import FolderWatcher
from .recycle_bin import send_to_recycle_bin

