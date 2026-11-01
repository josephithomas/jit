"""Visual rule engine supporting File Juggler style conditional file actions and templating."""
import os
import re
import time
import json
import fnmatch
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from .classifier import get_file_category, get_date_brackets, get_size_bracket
from .content_inspector import ContentInspector


@dataclass
class Condition:
    field: str  # 'filename', 'extension', 'category', 'size', 'date_modified', 'date_created', 'content', 'camera'
    operator: str  # 'contains', 'not_contains', 'equals', 'not_equals', 'starts_with', 'ends_with', 'regex', 'gt', 'lt', 'older_than_days', 'newer_than_days'
    value: Any = ""
    value2: Any = ""

    def evaluate(self, file_path: str, stats: os.stat_result) -> bool:
        base_name = os.path.basename(file_path)
        name_only, ext = os.path.splitext(base_name)
        ext_clean = ext.lower().lstrip('.')

        # Field retrieval
        if self.field == 'filename':
            target_val = base_name.lower()
            query_val = str(self.value).lower()
        elif self.field == 'extension':
            target_val = ext_clean
            query_val = str(self.value).lower().lstrip('.')
        elif self.field == 'category':
            target_val = get_file_category(base_name).lower()
            query_val = str(self.value).lower()
        elif self.field == 'size':
            target_val = stats.st_size
            try:
                query_val = float(self.value)
            except (ValueError, TypeError):
                query_val = 0.0
        elif self.field in ('date_modified', 'date_created'):
            ts = stats.st_mtime if self.field == 'date_modified' else stats.st_ctime
            target_val = ts
            try:
                query_val = float(self.value)
            except (ValueError, TypeError):
                query_val = 0.0
        elif self.field == 'content':
            # PyMuPDF, docx, or txt search
            return ContentInspector.matches_content_query(
                file_path, 
                str(self.value), 
                is_regex=(self.operator == 'regex')
            )
        elif self.field == 'camera':
            meta = ContentInspector.extract_image_metadata(file_path)
            target_val = meta.get('camera', '').lower()
            query_val = str(self.value).lower()
        else:
            return False

        # Operator evaluation
        if self.operator == 'contains':
            return str(query_val) in str(target_val)
        elif self.operator == 'not_contains':
            return str(query_val) not in str(target_val)
        elif self.operator == 'equals':
            return str(target_val) == str(query_val)
        elif self.operator == 'not_equals':
            return str(target_val) != str(query_val)
        elif self.operator == 'starts_with':
            return str(target_val).startswith(str(query_val))
        elif self.operator == 'ends_with':
            return str(target_val).endswith(str(query_val))
        elif self.operator == 'regex':
            try:
                return bool(re.search(str(self.value), str(target_val), re.IGNORECASE))
            except re.error:
                return False
        elif self.operator == 'wildcard':
            return fnmatch.fnmatch(str(target_val), str(query_val))
        elif self.operator == 'gt':
            try:
                return float(target_val) > float(query_val)
            except (ValueError, TypeError):
                return False
        elif self.operator == 'lt':
            try:
                return float(target_val) < float(query_val)
            except (ValueError, TypeError):
                return False
        elif self.operator == 'older_than_days':
            now = time.time()
            age_days = (now - float(target_val)) / 86400.0
            return age_days >= float(query_val)
        elif self.operator == 'newer_than_days':
            now = time.time()
            age_days = (now - float(target_val)) / 86400.0
            return age_days <= float(query_val)

        return False


@dataclass
class RuleAction:
    action_type: str = 'move'  # 'move', 'copy', 'rename', 'recycle', 'extract'
    target_folder: str = ""    # Template path or fixed path
    rename_pattern: str = ""   # e.g. "{name}_{date}.{ext}"
    overwrite_mode: str = "rename_new"  # 'rename_new', 'overwrite', 'skip'


@dataclass
class Rule:
    name: str
    id: str = ""
    enabled: bool = True
    match_all: bool = True  # True: AND, False: OR
    conditions: List[Condition] = field(default_factory=list)
    action: RuleAction = field(default_factory=RuleAction)

    def matches(self, file_path: str) -> bool:
        if not self.enabled or not self.conditions:
            return False

        try:
            stats = os.stat(file_path)
        except OSError:
            return False

        if self.match_all:
            return all(cond.evaluate(file_path, stats) for cond in self.conditions)
        else:
            return any(cond.evaluate(file_path, stats) for cond in self.conditions)


class RuleEngine:
    """Manages loading, saving, testing, and matching rules."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.rules: List[Rule] = []
        if self.config_file and os.path.exists(self.config_file):
            self.load()
        else:
            self._init_default_rules()

    def _init_default_rules(self):
        """Creates practical, high-value default rules."""
        self.rules = [
            Rule(
                id="default_invoices",
                name="Invoices & Receipts to Accounting",
                enabled=True,
                match_all=False,
                conditions=[
                    Condition(field='filename', operator='contains', value='invoice'),
                    Condition(field='filename', operator='contains', value='receipt'),
                    Condition(field='content', operator='contains', value='Invoice'),
                    Condition(field='content', operator='contains', value='Receipt')
                ],
                action=RuleAction(
                    action_type='move',
                    target_folder='Finance & Receipts/{year}',
                    overwrite_mode='rename_new'
                )
            ),
            Rule(
                id="default_screenshots",
                name="Sort Screenshots by Month",
                enabled=True,
                match_all=True,
                conditions=[
                    Condition(field='filename', operator='contains', value='screenshot')
                ],
                action=RuleAction(
                    action_type='move',
                    target_folder='Screenshots/{year}/{month}',
                    overwrite_mode='rename_new'
                )
            ),
            Rule(
                id="default_installers",
                name="Move Installers & Setups",
                enabled=True,
                match_all=False,
                conditions=[
                    Condition(field='extension', operator='equals', value='exe'),
                    Condition(field='extension', operator='equals', value='msi')
                ],
                action=RuleAction(
                    action_type='move',
                    target_folder='Installers',
                    overwrite_mode='rename_new'
                )
            )
        ]

    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self.save()

    def remove_rule(self, rule_id: str):
        self.rules = [r for r in self.rules if r.id != rule_id]
        self.save()

    def find_matching_rule(self, file_path: str) -> Optional[Rule]:
        for rule in self.rules:
            if rule.enabled and rule.matches(file_path):
                return rule
        return None

    def save(self):
        if not self.config_file:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
        data = []
        for r in self.rules:
            d = asdict(r)
            data.append(d)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not self.config_file or not os.path.exists(self.config_file):
            return
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = []
            for item in data:
                conds = [Condition(**c) for c in item.get('conditions', [])]
                act_data = item.get('action', {})
                act = RuleAction(**act_data) if act_data else RuleAction()
                rule = Rule(
                    name=item.get('name', 'Rule'),
                    id=item.get('id', str(time.time())),
                    enabled=item.get('enabled', True),
                    match_all=item.get('match_all', True),
                    conditions=conds,
                    action=act
                )
                loaded.append(rule)
            self.rules = loaded
        except Exception as e:
            print(f"Error loading rules config: {e}")
            self._init_default_rules()

