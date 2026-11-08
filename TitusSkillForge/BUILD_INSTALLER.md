# Build a Windows Installable Version of Titus SkillForge

You will end up with a normal **Setup.exe** that any Windows user can double-click.

---

## What the user gets

- Proper installer wizard (choose folder, Start Menu, Desktop icon)
- Titus logo as the installer + application icon
- Start Menu entry + optional Desktop shortcut
- Clean uninstall via Windows Settings → Apps

---

## One-command build (recommended)

1. Make sure these files are in your project folder:
   - `desktop_app.py`
   - `make_icon.py`
   - `build_installer.bat`
   - `setup.iss`
   - `assets/` (with logos)
   - `static/index.html`

2. Double-click or run:

```cmd
build_installer.bat
```

This will:

1. Create/update the virtual environment  
2. Install all dependencies  
3. Generate `assets\icon.ico` if missing  
4. Build `dist\TitusSkillForge.exe`  
5. Compile the installer (if Inno Setup is installed)

### Output

| File | Purpose |
|------|---------|
| `dist\TitusSkillForge.exe` | Portable single-file version |
| `Output\TitusSkillForge-Setup-1.0.0.exe` | **Windows Installer** (give this to users) |

---

## Install Inno Setup (one-time)

Download the free installer from:

https://jrsoftware.org/isinfo.php

Install the default version (Inno Setup 6).  
After installation, simply run `build_installer.bat` again — it will detect ISCC.exe automatically.

---

## Alternative: NSIS

If you prefer NSIS instead of Inno Setup:

1. Install NSIS → https://nsis.sourceforge.io  
2. Build the EXE first: `build_exe.bat`  
3. Right-click `setup.nsi` → **Compile NSIS Script**  
   (or run `makensis setup.nsi`)

You will get `TitusSkillForge-Setup-1.0.0.exe` in the same folder.

---

## Quick checklist before distributing

- [ ] `python make_icon.py` succeeded (icon.ico exists)
- [ ] `dist\TitusSkillForge.exe` launches and shows the UI
- [ ] Installer runs on a clean Windows machine
- [ ] Start Menu shortcut works
- [ ] Uninstall removes the program cleanly

---

## File size note

The final Setup.exe is typically **90–160 MB**.  
This is normal — it contains the full Python runtime + PyQt6 WebEngine so the end user needs nothing else installed.
