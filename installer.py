"""
Universal Skill.md Installer and Exporter for SkillForge.
Installs generated skills directly into Antigravity, Claude, Grok, or packages as a ZIP bundle.
"""

from __future__ import annotations
import os
import io
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional


class SkillInstaller:
    """Handles local directory deployment and package archiving."""

    DEFAULT_ANTIGRAVITY_DIR = os.path.expanduser(r"~\.gemini\config\skills")
    DEFAULT_CLAUDE_DIR = os.path.expanduser(r"~\.claude\skills")
    DEFAULT_GROK_DIR = os.path.expanduser(r"~\.grok\skills")

    @classmethod
    def install_to_antigravity(cls, skill_name: str, markdown_content: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
        target_base = Path(base_dir) if base_dir else Path(cls.DEFAULT_ANTIGRAVITY_DIR)
        skill_dir = target_base / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        file_path = skill_dir / "SKILL.md"
        file_path.write_text(markdown_content, encoding="utf-8")

        return {
            "success": True,
            "target": "antigravity",
            "installed_path": str(file_path),
            "directory": str(skill_dir)
        }

    @classmethod
    def install_to_claude(cls, skill_name: str, markdown_content: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
        target_base = Path(base_dir) if base_dir else Path(cls.DEFAULT_CLAUDE_DIR)
        skill_dir = target_base / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        file_path = skill_dir / "SKILL.md"
        file_path.write_text(markdown_content, encoding="utf-8")

        return {
            "success": True,
            "target": "claude",
            "installed_path": str(file_path),
            "directory": str(skill_dir)
        }

    @classmethod
    def install_to_workspace(cls, skill_name: str, markdown_content: str, workspace_dir: str) -> Dict[str, Any]:
        ws = Path(workspace_dir)
        paths = []
        for agent_sub in [".grok/skills", ".claude/skills"]:
            dir_target = ws / agent_sub / skill_name
            dir_target.mkdir(parents=True, exist_ok=True)
            fpath = dir_target / "SKILL.md"
            fpath.write_text(markdown_content, encoding="utf-8")
            paths.append(str(fpath))

        return {
            "success": True,
            "target": "workspace",
            "installed_paths": paths
        }

    @classmethod
    def create_zip_package(cls, skill_name: str, markdown_content: str) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{skill_name}/SKILL.md", markdown_content)
            
            readme_text = f"""# {skill_name}

Universal Agent Skill package compatible with:
- Claude Code & Claude Desktop (`~/.claude/skills/{skill_name}/`)
- Google Antigravity (`~/.gemini/config/skills/{skill_name}/`)
- xAI Grok (`.grok/skills/{skill_name}/`)
- OpenAI ChatGPT / Custom GPTs (instructions body)
- Google Gemini System Instructions

## Installation

### For Antigravity:
Copy the `{skill_name}` directory to `~/.gemini/config/skills/{skill_name}/`.

### For Claude:
Copy the `{skill_name}` directory to `~/.claude/skills/{skill_name}/`.

### For Grok:
Copy the `{skill_name}` directory into your repository under `.grok/skills/{skill_name}/`.

Generated with Titus SkillForge — Universal Agent Engine.
Anchored to: https://github.com/josephithomas/jit
"""
            zf.writestr(f"{skill_name}/README.md", readme_text)
            zf.writestr(f"{skill_name}/scripts/.keep", "")

        buffer.seek(0)
        return buffer.getvalue()
