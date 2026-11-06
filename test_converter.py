"""
Unit tests for Titus SkillForge Universal.
Verifies DocumentParser, SkillSynthesizer, SkillValidator, and SkillInstaller.
"""

from __future__ import annotations
import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from parser import DocumentParser
from synthesizer import SkillSynthesizer
from validator import SkillValidator
from installer import SkillInstaller


class TestSkillForge(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(SkillSynthesizer.slugify("My Test Skill"), "my-test-skill")
        self.assertEqual(SkillSynthesizer.slugify("AWS_Cost_Optimizer_101!"), "aws-cost-optimizer-101")
        self.assertEqual(SkillSynthesizer.slugify(""), "universal-skill")

    def test_synthesizer_basic(self):
        sample = """
        Procedure for API Security Auditing.
        1. Scan endpoint headers.
        2. Verify JWT signature validity.
        3. Check CORS origin restrictions.
        Boundaries: Read-only audits only. Never inject destructive SQL payloads.
        """
        synth = SkillSynthesizer.synthesize(
            raw_text=sample,
            skill_name="api-security-auditor",
            description="Automated API vulnerability and CORS auditing tool."
        )
        self.assertIn("name: api-security-auditor", synth["markdown"])
        self.assertIn("## Operational Rules & Boundaries", synth["markdown"])
        self.assertIn("## Execution Workflow", synth["markdown"])
        self.assertIn("Titus SkillForge", synth["markdown"])

    def test_validator(self):
        sample = """---
name: sample-auditor
description: Valid sample auditor for test harness.
tags: [security, audit]
version: 1.0.0
author: Titus SkillForge
---

# sample-auditor

## Purpose & Overview
Detailed purpose statement.

## Operational Rules & Boundaries
- Boundary 1: Strict read-only.
- Boundary 2: No destructive execution.

## Execution Workflow
1. Step one.
2. Step two.
3. Step three.

## Input & Output Contracts
Input: json
Output: markdown report
"""
        res = SkillValidator.validate_content(sample)
        self.assertTrue(res["valid"])
        self.assertGreaterEqual(res["score"], 80)
        self.assertTrue(res["compatibility"]["claude"]["compatible"])
        self.assertTrue(res["compatibility"]["grok"]["compatible"])
        self.assertTrue(res["compatibility"]["gemini"]["compatible"])

    def test_parser_plaintext(self):
        text_content = b"Simple specification text for testing parser."
        res = DocumentParser.parse_file(text_content, "spec.txt")
        self.assertEqual(res["format"], "text")
        self.assertIn("Simple specification", res["text"])

    def test_zip_creation(self):
        content = "---\nname: demo-skill\ndescription: A demo skill.\n---\n# demo\n"
        zip_bytes = SkillInstaller.create_zip_package("demo-skill", content)
        self.assertGreater(len(zip_bytes), 100)


if __name__ == "__main__":
    unittest.main()
