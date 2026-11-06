"""
Installer & Shortcut Creator for Titus SkillForge Studio.
Generates:
1. Native Windows Shortcut (.lnk) on Desktop pointing to pythonw.exe (no black console window)
2. Desktop batch launcher (.bat) for instant 1-click fallback
3. Start Menu shortcut
4. Mirrors codebase to scratch directory for backwards-compatibility
"""

from __future__ import annotations
import os
import sys
import shutil
from pathlib import Path

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

APP_DIR = Path(r"C:\Users\Joseph I Thomas\universal-skill-creator")
SCRATCH_DIR = Path(r"C:\Users\Joseph I Thomas\.gemini\antigravity\scratch\universal-skill-creator")
DESKTOP_DIR = Path(r"C:\Users\Joseph I Thomas\Desktop")
START_MENU_DIR = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"))

PYTHON_EXE = sys.executable
PYTHONW_EXE = Path(sys.executable).parent / "pythonw.exe"
if not PYTHONW_EXE.exists():
    PYTHONW_EXE = Path(PYTHON_EXE)

MAIN_SCRIPT = APP_DIR / "desktop_app.py"
ICON_PATH = APP_DIR / "assets" / "icon.ico"


def create_windows_shortcut(target_path: Path, shortcut_path: Path, arguments: str = "", work_dir: Path = None, icon_path: Path = None, description: str = ""):
    """Create a Windows .lnk shortcut using powershell WScript.Shell without brittle external scripts."""
    import subprocess
    work_dir_str = str(work_dir) if work_dir else str(target_path.parent)
    icon_str = f"'{icon_path}, 0'" if icon_path and icon_path.exists() else "''"
    
    ps_cmd = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{target_path}'
    $Shortcut.Arguments = '{arguments}'
    $Shortcut.WorkingDirectory = '{work_dir_str}'
    $Shortcut.Description = '{description}'
    if ('{icon_path}' -ne '' -and (Test-Path '{icon_path}')) {{
        $Shortcut.IconLocation = '{icon_path}, 0'
    }}
    $Shortcut.Save()
    """
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)


def create_batch_launcher(bat_path: Path, app_directory: Path):
    """Create a direct 1-click batch launcher."""
    content = f"""@echo off
title Titus SkillForge Studio Launcher
cd /d "{app_directory}"
start "" "{PYTHONW_EXE}" "{app_directory / 'desktop_app.py'}"
exit
"""
    bat_path.write_text(content, encoding="utf-8")


def mirror_to_scratch():
    """Copy all files to the scratch directory so any old references work seamlessly."""
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    for item in APP_DIR.glob("**/*"):
        if item.is_file():
            rel = item.relative_to(APP_DIR)
            target = SCRATCH_DIR / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def main():
    print("=" * 65)
    print("  Titus SkillForge Studio — Windows Desktop Installer & Setup")
    print("=" * 65)

    if not APP_DIR.exists():
        print(f"[!] Target directory {APP_DIR} does not exist.")
        sys.exit(1)

    print(f"[*] Application directory: {APP_DIR}")
    print(f"[*] Python interpreter: {PYTHONW_EXE}")
    print(f"[*] Main entrypoint: {MAIN_SCRIPT}")
    print(f"[*] Icon asset: {ICON_PATH}")

    # 1. Create desktop shortcut (.lnk)
    desktop_lnk = DESKTOP_DIR / "Titus SkillForge Studio.lnk"
    print(f"[*] Creating Desktop shortcut: {desktop_lnk.name}...")
    create_windows_shortcut(
        target_path=PYTHONW_EXE,
        shortcut_path=desktop_lnk,
        arguments=f'"{MAIN_SCRIPT}"',
        work_dir=APP_DIR,
        icon_path=ICON_PATH,
        description="Titus SkillForge Studio — Universal SKILL.md Creator"
    )
    print(f"[✓] Created: {desktop_lnk}")

    # 2. Create desktop batch launcher (.bat)
    desktop_bat = DESKTOP_DIR / "Launch SkillForge Studio.bat"
    create_batch_launcher(desktop_bat, APP_DIR)
    print(f"[✓] Created fallback Desktop launcher: {desktop_bat.name}")

    # 3. Create app directory batch launcher (.bat)
    app_bat = APP_DIR / "SkillForge.bat"
    create_batch_launcher(app_bat, APP_DIR)
    print(f"[✓] Created internal batch launcher: {app_bat.name}")

    # 4. Start Menu shortcut
    if START_MENU_DIR.exists():
        start_menu_lnk = START_MENU_DIR / "Titus SkillForge Studio.lnk"
        create_windows_shortcut(
            target_path=PYTHONW_EXE,
            shortcut_path=start_menu_lnk,
            arguments=f'"{MAIN_SCRIPT}"',
            work_dir=APP_DIR,
            icon_path=ICON_PATH,
            description="Titus SkillForge Studio — Universal SKILL.md Creator"
        )
        print(f"[✓] Created Start Menu shortcut: {start_menu_lnk}")

    # 5. Mirror to scratch folder for compatibility
    print("[*] Mirroring files to scratch directory for compatibility...")
    mirror_to_scratch()
    print(f"[✓] Mirrored to: {SCRATCH_DIR}")

    # Clean up any broken VBScript file that caused error 800A0401
    broken_vbs = SCRATCH_DIR / "SkillForge_Launcher.vbs"
    if broken_vbs.exists():
        try:
            broken_vbs.unlink()
            print("[✓] Removed obsolete VBScript file.")
        except Exception:
            pass

    print("\n" + "=" * 65)
    print("  [SUCCESS] Titus SkillForge Studio is fully installed and ready!")
    print("  Shortcut available on your Desktop: 'Titus SkillForge Studio'")
    print("=" * 65)


if __name__ == "__main__":
    main()
