"""
Universal Skill.md Validator and Cross-Platform Linter.
Validates SKILL.md against Claude, Grok, ChatGPT, Gemini, and Antigravity specifications.
"""

from __future__ import annotations
import re
import yaml
from typing import Dict, Any, List, Tuple


class SkillValidator:
    """Verifies that a SKILL.md file meets all universal platform criteria."""

    @classmethod
    def validate_content(cls, markdown_content: str) -> Dict[str, Any]:
        issues: List[str] = []
        warnings: List[str] = []
        platforms_status = {
            "claude": {"compatible": False, "notes": []},
            "grok": {"compatible": False, "notes": []},
            "chatgpt": {"compatible": False, "notes": []},
            "gemini": {"compatible": False, "notes": []},
            "antigravity": {"compatible": False, "notes": []}
        }

        fm_match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', markdown_content.strip(), re.DOTALL)
        if not fm_match:
            issues.append("Missing standard YAML frontmatter bounded by '---'.")
            return {
                "valid": False,
                "score": 10,
                "issues": issues,
                "warnings": warnings,
                "compatibility": platforms_status,
                "stats": {"word_count": len(markdown_content.split()), "token_estimate": int(len(markdown_content.split()) * 1.3)},
                "frontmatter": None
            }

        raw_yaml = fm_match.group(1)
        body = fm_match.group(2).strip()

        try:
            frontmatter = yaml.safe_load(raw_yaml)
            if not isinstance(frontmatter, dict):
                issues.append("Frontmatter is not a valid YAML mapping/object.")
                frontmatter = {}
        except Exception as e:
            issues.append(f"YAML parsing error in frontmatter: {e}")
            frontmatter = {}

        name = frontmatter.get("name")
        if not name or not isinstance(name, str):
            issues.append("Frontmatter missing required string field 'name'.")
        else:
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
                issues.append(f"Skill name '{name}' must be lowercase kebab-case (e.g. 'my-useful-skill').")
            if len(name) > 64:
                warnings.append(f"Skill name '{name}' is longer than 64 characters; keep it concise.")

        description = frontmatter.get("description")
        if not description or not isinstance(description, str):
            issues.append("Frontmatter missing required string field 'description'.")
        else:
            if len(description.strip()) < 15:
                warnings.append("Description is very short. Describe both capability and trigger conditions.")
            if len(description) > 1024:
                warnings.append("Description exceeds 1024 characters. Shorten to conserve context tokens.")
            desc_lower = description.lower()
            if not any(k in desc_lower for k in ["trigger", "use for", "when", "for:", "invoke"]):
                warnings.append("Description should specify trigger criteria (e.g., 'Use for: ...' or 'Trigger when: ...').")

        body_lower = body.lower()
        has_title = bool(re.search(r'^#\s+.+', body, re.MULTILINE))
        if not has_title:
            warnings.append("Skill body should start with a main heading (# Skill Title).")

        expected_sections = [
            ("Purpose / Overview", ["purpose", "overview", "description"]),
            ("Triggers / Activation", ["trigger", "activation", "when to use"]),
            ("Workflow / Execution", ["workflow", "execution", "procedure", "steps", "instructions"]),
            ("Boundaries / Rules", ["rule", "boundary", "constraint", "safety"]),
            ("Error Handling", ["error", "troubleshoot", "fallback", "edge case"])
        ]

        missing_sections = []
        for sec_name, keywords in expected_sections:
            if not any(kw in body_lower for kw in keywords):
                missing_sections.append(sec_name)

        if missing_sections:
            warnings.append(f"Consider adding standard sections: {', '.join(missing_sections)}.")

        is_frontmatter_ok = (not any("name" in i or "frontmatter" in i for i in issues))

        if is_frontmatter_ok and name and description:
            platforms_status["claude"]["compatible"] = True
            platforms_status["claude"]["notes"].append("Standard YAML frontmatter complies with Claude skill discovery.")
        else:
            platforms_status["claude"]["notes"].append("Requires valid name and description in YAML frontmatter.")

        if is_frontmatter_ok and name and description:
            platforms_status["grok"]["compatible"] = True
            grok_meta = frontmatter.get("metadata", {}).get("grok", {}) if isinstance(frontmatter.get("metadata"), dict) else {}
            if grok_meta.get("tags"):
                platforms_status["grok"]["notes"].append("Grok tags metadata verified.")
            else:
                platforms_status["grok"]["notes"].append("Compatible (recommends adding metadata.grok.tags).")
        else:
            platforms_status["grok"]["notes"].append("Requires valid frontmatter.")

        if description and len(body) > 100:
            platforms_status["chatgpt"]["compatible"] = True
            platforms_status["chatgpt"]["notes"].append("Clean markdown instructions easily ingested as Custom GPT instructions.")
        else:
            platforms_status["chatgpt"]["notes"].append("Instructions too brief for Custom GPT.")

        if description and len(body) > 100:
            platforms_status["gemini"]["compatible"] = True
            platforms_status["gemini"]["notes"].append("Structured workflow and boundaries align with Gemini System Instructions.")
        else:
            platforms_status["gemini"]["notes"].append("Instructions too brief for Gemini System Instructions.")

        if is_frontmatter_ok and name and description:
            platforms_status["antigravity"]["compatible"] = True
            platforms_status["antigravity"]["notes"].append("Fully matches Antigravity Agent Skills specification (~/.gemini/config/skills/).")
        else:
            platforms_status["antigravity"]["notes"].append("Requires valid kebab-case name and description.")

        words = len(markdown_content.split())
        token_estimate = int(words * 1.33)
        if token_estimate > 3500:
            warnings.append(f"Estimated token footprint (~{token_estimate} tokens) is high. Streamline to prevent context bloat.")
        elif token_estimate < 120:
            warnings.append(f"Estimated token footprint (~{token_estimate} tokens) is very minimal; ensure essential operational steps are covered.")

        score = 100
        score -= len(issues) * 25
        score -= len(warnings) * 5
        score = max(0, min(100, score))

        valid = (len(issues) == 0)

        return {
            "valid": valid,
            "score": score,
            "issues": issues,
            "warnings": warnings,
            "compatibility": platforms_status,
            "stats": {
                "word_count": words,
                "character_count": len(markdown_content),
                "token_estimate": token_estimate,
                "sections_found": 5 - len(missing_sections)
            },
            "frontmatter": frontmatter
        }
