@echo off
title Titus SkillForge — Build Windows Installer
cd /d "%~dp0"

echo ============================================================
echo   Titus SkillForge Studio
echo   Building Standalone EXE + Windows Installer
echo ============================================================
echo.

:: ----------------------------------------------------------
:: 1. Check Python
:: ----------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: ----------------------------------------------------------
:: 2. Virtual environment
:: ----------------------------------------------------------
echo [*] Preparing virtual environment...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [*] Installing / updating dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller PyQt6 PyQt6-WebEngine Pillow

:: ----------------------------------------------------------
:: 3. Ensure icon exists
:: ----------------------------------------------------------
if not exist "assets" mkdir assets
if not exist "assets\icon.ico" (
    echo [*] Generating assets\icon.ico from Titus logo...
    python make_icon.py
    if errorlevel 1 (
        echo [ERROR] Could not create icon.ico
        echo         Place titus-logo-256.png (or titus-logo.png) in assets\
        pause
        exit /b 1
    )
)

if not exist "static\index.html" (
    echo [ERROR] static\index.html is missing.
    echo         The web UI will be blank without it.
    pause
    exit /b 1
)

:: ----------------------------------------------------------
:: 4. Build the single-file EXE
:: ----------------------------------------------------------
echo.
echo [*] Building TitusSkillForge.exe (this may take 1-3 minutes)...
echo.

pyinstaller --noconfirm --clean ^
    --name "TitusSkillForge" ^
    --windowed ^
    --onefile ^
    --icon "assets\icon.ico" ^
    --add-data "static;static" ^
    --add-data "assets;assets" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.protocols.websockets" ^
    --hidden-import "uvicorn.protocols.websockets.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "pydantic" ^
    --hidden-import "yaml" ^
    --collect-all "uvicorn" ^
    --collect-all "fastapi" ^
    --collect-all "starlette" ^
    desktop_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

if not exist "dist\TitusSkillForge.exe" (
    echo [ERROR] dist\TitusSkillForge.exe was not created.
    pause
    exit /b 1
)

echo [OK] EXE ready: dist\TitusSkillForge.exe

:: ----------------------------------------------------------
:: 5. Build the Windows Installer with Inno Setup
:: ----------------------------------------------------------
echo.
echo [*] Looking for Inno Setup compiler...

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo.
    echo [WARNING] Inno Setup 6 not found.
    echo.
    echo The standalone EXE is ready:
    echo     %cd%\dist\TitusSkillForge.exe
    echo.
    echo To create a full installer later:
    echo   1. Download Inno Setup 6 from https://jrsoftware.org/isinfo.php
    echo   2. Install it
    echo   3. Run this script again, or open setup.iss in Inno Setup
    echo.
    explorer dist
    pause
    exit /b 0
)

echo [*] Compiling installer with Inno Setup...
"%ISCC%" setup.iss

if errorlevel 1 (
    echo.
    echo [ERROR] Inno Setup compilation failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS
echo.
echo   Standalone EXE :
echo     %cd%\dist\TitusSkillForge.exe
echo.
echo   Windows Installer :
echo     %cd%\Output\TitusSkillForge-Setup-1.0.0.exe
echo.
echo   Users only need to run the Setup EXE.
echo   It will install the app, create Start Menu entry,
echo   optional Desktop shortcut, and support clean uninstall.
echo ============================================================
echo.

if exist "Output" explorer Output
pause
