@echo off
title Titus OmniSort Pro - Build Release (Executable + Installer)
color 0B
echo.
echo ====================================================================
echo   TITUS OMNISORT PRO - RELEASE COMPILER
echo   Building Portable Executable (.exe) and Windows Setup Installer
echo ====================================================================
echo.

cd /d "%~dp0"

echo [1/3] Compiling Standalone Portable Executable with PyInstaller...
python -m PyInstaller --noconfirm --clean "Titus_OmniSort_Pro.spec"

if not exist "dist\Titus_OmniSort_Pro.exe" (
    echo.
    echo [ERROR] PyInstaller failed to produce dist\Titus_OmniSort_Pro.exe
    pause
    exit /b 1
)

echo.
echo [2/3] Standalone Executable built successfully:
echo       %~dp0dist\Titus_OmniSort_Pro.exe
echo.

echo [3/3] Compiling Windows Setup Installer with Inno Setup Compiler...
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if exist "%ISCC%" (
    "%ISCC%" "Titus_OmniSort_Pro.iss"
    if errorlevel 1 (
        echo [ERROR] Inno Setup compilation failed.
        pause
        exit /b 1
    )
    echo.
    echo [SUCCESS] Windows Setup Installer created:
    echo           %~dp0Output\Titus_OmniSort_Pro_Setup.exe
) else (
    echo [WARNING] Inno Setup compiler ISCC.exe not found.
)

echo.
echo ====================================================================
echo   BUILD COMPLETED!
echo   1. Portable Executable: %~dp0dist\Titus_OmniSort_Pro.exe
echo   2. Setup Installer:     %~dp0Output\Titus_OmniSort_Pro_Setup.exe
echo ====================================================================
echo.

