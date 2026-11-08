@echo off
title Titus SkillForge — Build Standalone EXE
cd /d "%~dp0"

echo ============================================================
echo   Titus SkillForge Studio — Building Windows EXE
echo   (Titus icon baked into the EXE)
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

echo [*] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [*] Installing build dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller PyQt6 PyQt6-WebEngine

if not exist "assets\icon.ico" (
    echo [*] assets\icon.ico not found — generating from Titus logo...
    if not exist "assets" mkdir assets
    python make_icon.py
    if errorlevel 1 (
        echo [ERROR] Could not create assets\icon.ico
        echo         Make sure assets\titus-logo-256.png or assets\titus-logo.png exists.
        pause
        exit /b 1
    )
)

echo.
echo [*] Building single-file EXE with baked-in Titus icon...
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
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS — Titus icon is baked into the EXE
echo.
echo   File: %cd%\dist\TitusSkillForge.exe
echo ============================================================
echo.
explorer dist
pause
