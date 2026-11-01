"""Comprehensive test suite for OmniSort Pro core modules."""
import os
import shutil
import tempfile
import unittest

from sorter_app.core.classifier import (
    get_file_category, get_size_bracket, get_date_brackets, 
    get_alphabetical_bucket, format_file_size
)
from sorter_app.core.rule_engine import RuleEngine, Rule, Condition, RuleAction
from sorter_app.core.undo_manager import UndoManager
from sorter_app.core.duplicate_finder import DuplicateFinder
from sorter_app.core.organizer_engine import OrganizerEngine
from sorter_app.core.content_inspector import ContentInspector


class TestOmniSortCore(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="omnisort_test_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_classifier(self):
        self.assertEqual(get_file_category("report.pdf"), "Documents")
        self.assertEqual(get_file_category("sheet.xlsx"), "Spreadsheets")
        self.assertEqual(get_file_category("photo.jpg"), "Images")
        self.assertEqual(get_file_category("song.mp3"), "Audio")
        self.assertEqual(get_file_category("movie.mp4"), "Video")
        self.assertEqual(get_file_category("archive.zip"), "Archives")
        self.assertEqual(get_file_category("script.py"), "Development")
        self.assertEqual(get_file_category("setup.exe"), "Executables")

        self.assertEqual(get_size_bracket(500), "Tiny (< 100 KB)")
        self.assertEqual(get_size_bracket(500 * 1024), "Small (100 KB - 1 MB)")
        self.assertEqual(get_size_bracket(10 * 1024 * 1024), "Medium (1 MB - 50 MB)")

        self.assertEqual(get_alphabetical_bucket("Apple.txt"), "A - E")
        self.assertEqual(get_alphabetical_bucket("Zebra.txt"), "U - Z")
        self.assertEqual(get_alphabetical_bucket("123.txt"), "0-9 & Symbols")

    def test_content_inspector(self):
        # Create text file
        txt_path = os.path.join(self.test_dir, "sample_invoice.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Invoice #10042\nTotal Amount Due: $1,250.00\nClient: ACME Corp")

        self.assertTrue(ContentInspector.matches_content_query(txt_path, "Invoice"))
        self.assertTrue(ContentInspector.matches_content_query(txt_path, "acme", is_regex=False))
        self.assertTrue(ContentInspector.matches_content_query(txt_path, r"\$1,250", is_regex=True))
        self.assertFalse(ContentInspector.matches_content_query(txt_path, "SecretContract"))

    def test_rule_engine(self):
        config_path = os.path.join(self.test_dir, "rules.json")
        re = RuleEngine(config_file=config_path)

        # Create a rule for test logs
        custom_rule = Rule(
            id="rule_logs",
            name="Log Files Rule",
            enabled=True,
            match_all=True,
            conditions=[Condition(field='extension', operator='equals', value='log')],
            action=RuleAction(action_type='move', target_folder='Logs')
        )
        re.add_rule(custom_rule)

        log_file = os.path.join(self.test_dir, "app_debug.log")
        with open(log_file, "w") as f:
            f.write("2026-11-01 Test Log")

        matched = re.find_matching_rule(log_file)
        self.assertIsNotNone(matched)
        self.assertEqual(matched.name, "Log Files Rule")

    def test_organizer_preview_and_execution(self):
        undo_mgr = UndoManager(history_file=os.path.join(self.test_dir, "history.json"))
        engine = OrganizerEngine(undo_manager=undo_mgr)

        # Create test files
        f1 = os.path.join(self.test_dir, "doc1.pdf")
        f2 = os.path.join(self.test_dir, "img1.png")
        for f in (f1, f2):
            with open(f, "w") as fp:
                fp.write("dummy content")

        # Dry Run Preview
        ops = engine.generate_preview(
            file_paths=[f1, f2],
            preset_mode='category',
            action='move'
        )
        self.assertEqual(len(ops), 2)
        self.assertTrue(ops[0].target_path.endswith(os.path.join("Documents", "doc1.pdf")))
        self.assertTrue(ops[1].target_path.endswith(os.path.join("Images", "img1.png")))

        # Execution
        res = engine.execute_operations(ops, "Test Run", self.test_dir)
        self.assertTrue(res['success'])
        self.assertEqual(res['completed'], 2)
        self.assertFalse(os.path.exists(f1))
        self.assertTrue(os.path.exists(ops[0].target_path))

        # Rollback Undo
        batch_id = res['batch_id']
        rb_res = undo_mgr.rollback_batch(batch_id)
        self.assertTrue(rb_res['success'])
        self.assertEqual(rb_res['restored'], 2)
        # Should be back at original path!
        self.assertTrue(os.path.exists(f1))
        self.assertTrue(os.path.exists(f2))

    def test_duplicate_finder(self):
        dup_dir = os.path.join(self.test_dir, "dup_test")
        os.makedirs(dup_dir, exist_ok=True)

        content = b"Exact identical binary contents for duplicate test 123456789"
        d1 = os.path.join(dup_dir, "file1.txt")
        d2 = os.path.join(dup_dir, "file2_copy.txt")
        unique = os.path.join(dup_dir, "file_unique.txt")

        with open(d1, "wb") as f: f.write(content)
        with open(d2, "wb") as f: f.write(content)
        with open(unique, "wb") as f: f.write(b"Unique content")

        finder = DuplicateFinder()
        groups = finder.scan_directory(dup_dir, recursive=False)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0].items), 2)


if __name__ == '__main__':
    unittest.main()

