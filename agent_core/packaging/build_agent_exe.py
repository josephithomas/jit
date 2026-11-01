"""Standalone Executable Packaging Utility for Autonomous Agents.

Compiles background agents into single-file Windows executables (.exe)
using PyInstaller with options for:
- Windowless silent background service (--headless)
- Interactive CLI agent (--cli)
- Custom icon and metadata
"""

import os
import sys
import argparse
import subprocess


def package_agent(
    entry_script: str = "run_agent.py",
    app_name: str = "TitusAutonomousAgent",
    headless: bool = True,
    icon_path: str = "app_icon.ico",
) -> bool:
    """Build a standalone single-file .exe for the agent."""
    if not os.path.exists(entry_script):
        print(f"Error: Entry script '{entry_script}' not found.")
        return False

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--onefile",
        "--name",
        app_name,
    ]

    if headless:
        cmd.append("--noconsole")

    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    cmd.append(entry_script)

    print(f"Executing packaging: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"\n[+] Successfully generated standalone executable at: dist/{app_name}.exe")
        return True
    else:
        print(f"\n[!] Packaging failed with return code {result.returncode}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package Autonomous Agent into Standalone EXE")
    parser.add_argument("--entry", default="agent_core/templates/sample_background_agent.py", help="Path to Python agent entrypoint")
    parser.add_argument("--name", default="AutonomousWorkerAgent", help="Output EXE name")
    parser.add_argument("--console", action="store_true", help="Keep console window open (default is headless)")

    args = parser.parse_args()
    package_agent(
        entry_script=args.entry,
        app_name=args.name,
        headless=not args.console,
    )
