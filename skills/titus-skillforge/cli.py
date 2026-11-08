"""
Command-line interface for Titus SkillForge Universal.
Convert files or text into valid SKILL.md directly from terminal.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from parser import DocumentParser
from synthesizer import SkillSynthesizer
from validator import SkillValidator
from installer import SkillInstaller


TITUS_BANNER = r"""
======================================================================
  _____ _ _             ____  _    _ _ _ _____                     
 |_   _(_) |_ _   _ ___/ ___|| | _(_) | |  ___|__  _ __ __ _  ___ 
   | | | | __| | | / __\___ \| |/ / | | | |_ / _ \| '__/ _` |/ _ \
   | | | | |_| |_| \__ \___) |   <| | | |  _| (_) | | | (_| |  __/
   |_| |_|\__|\__,_|___/____/|_|\_\_|_|_|_|  \___/|_|  \__, |\___|
                                                       |___/      
     Universal SKILL.md Studio & Cross-Platform Orchestrator
======================================================================
"""


def main():
    parser = argparse.ArgumentParser(
        description="Titus SkillForge: Convert documents, PDFs, Word files, or text into cross-platform SKILL.md files."
    )
    parser.add_argument("--input", "-i", type=str, help="Input file path (PDF, DOCX, PPTX, image, TXT, MD)")
    parser.add_argument("--text", "-t", type=str, help="Raw text string or prompt description")
    parser.add_argument("--name", "-n", type=str, help="Skill name (e.g. data-analyzer)")
    parser.add_argument("--desc", "-d", type=str, help="Short 1-2 sentence description")
    parser.add_argument("--output", "-o", type=str, default="SKILL.md", help="Output file path (default: SKILL.md)")
    parser.add_argument("--install", choices=["claude", "antigravity", "workspace"], help="Install directly to local agent folder")
    parser.add_argument("--zip", action="store_true", help="Generate ready-to-distribute .zip skill package")
    parser.add_argument("--validate-only", type=str, help="Validate an existing SKILL.md file and exit")

    args = parser.parse_args()

    print(TITUS_BANNER)

    if args.validate_only:
        val_path = Path(args.validate_only)
        if not val_path.exists():
            print(f"[!] Error: File {val_path} does not exist.")
            sys.exit(1)
        content = val_path.read_text(encoding="utf-8")
        res = SkillValidator.validate_content(content)
        print(f"Validation Score: {res['score']}/100")
        print(f"Valid: {res['valid']}")
        for p, ok in res.get("platforms", {}).items():
            print(f"  • {p.capitalize()}: {'✓ Compliant' if ok else '✗ Attention Needed'}")
        if res.get("errors"):
            print("\nErrors:")
            for err in res["errors"]:
                print(f"  - {err}")
        if res.get("warnings"):
            print("\nWarnings:")
            for warn in res["warnings"]:
                print(f"  - {warn}")
        sys.exit(0 if res["valid"] else 1)

    raw_text = ""
    skill_name = args.name

    if args.input:
        in_path = Path(args.input)
        if not in_path.exists():
            print(f"[!] Error: Input file '{in_path}' not found.")
            sys.exit(1)
        print(f"[*] Ingesting file: {in_path.name}...")
        parsed = DocumentParser.parse_file(in_path.read_bytes(), in_path.name)
        raw_text = parsed.get("text", "")
        if not skill_name:
            skill_name = in_path.stem.lower().replace(" ", "-")
        print(f"[✓] Extracted {len(raw_text)} characters (Format: {parsed.get('format')}).")
    elif args.text:
        raw_text = args.text
    else:
        print("[!] Error: You must provide either --input <file> or --text '<content>'.")
        parser.print_help()
        sys.exit(1)

    if not skill_name:
        skill_name = "universal-skill"

    print(f"[*] Synthesizing universal SKILL.md for '{skill_name}'...")
    synth = SkillSynthesizer.synthesize(
        raw_text=raw_text,
        skill_name=skill_name,
        description=args.desc
    )

    out_path = Path(args.output)
    out_path.write_text(synth["markdown"], encoding="utf-8")
    print(f"[✓] Successfully wrote SKILL.md to: {out_path.resolve()}")

    # Validate output
    val = SkillValidator.validate_content(synth["markdown"])
    print(f"[✓] Cross-Platform Quality Score: {val['score']}/100")
    for plat, ok in val.get("platforms", {}).items():
        print(f"    - {plat.capitalize()}: {'✓ READY' if ok else '✗ CHECK'}")

    if args.zip:
        zip_bytes = SkillInstaller.create_zip_package(synth["name"], synth["markdown"])
        zip_name = f"{synth['name']}-skill-package.zip"
        Path(zip_name).write_bytes(zip_bytes)
        print(f"[✓] Created distribution package: {zip_name}")

    if args.install:
        print(f"[*] Installing skill to {args.install}...")
        if args.install == "antigravity":
            inst_res = SkillInstaller.install_to_antigravity(synth["name"], synth["markdown"])
        elif args.install == "claude":
            inst_res = SkillInstaller.install_to_claude(synth["name"], synth["markdown"])
        elif args.install == "workspace":
            inst_res = SkillInstaller.install_to_workspace(synth["name"], synth["markdown"], str(Path.cwd()))
        print(f"[✓] Installation Result: {inst_res.get('message')}")
        print(f"    Path: {inst_res.get('path')}")

    print("\n[Done] Skill ready for deployment across Claude, Grok, ChatGPT, Gemini, and Antigravity.")


if __name__ == "__main__":
    main()
