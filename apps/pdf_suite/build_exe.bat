@echo off
title TSTC Professional PDF Suite - Build EXE
color 0A
echo.
echo  ================================================
echo   TSTC Professional PDF Suite v4.0
echo   Building standalone EXE with Titus logo icon
echo  ================================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install from https://www.python.org/downloads/
    echo Check "Add Python to PATH" during setup.
    pause
    exit /b 1
)

echo [1/4] Checking assets & dependencies...
set "ICON_ARG="
set "DATA_ARG="

if exist "titus.ico" (
    echo          Found: titus.ico
    set "ICON_ARG=--icon=titus.ico"
    set "DATA_ARG=--add-data titus.ico;."
)

if exist "logo.png" (
    echo          Found: logo.png
    if defined DATA_ARG (
        set "DATA_ARG=%DATA_ARG% --add-data logo.png;."
    ) else (
        set "DATA_ARG=--add-data logo.png;."
    )
)

echo [2/4] Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1

echo [3/4] Building standalone executable with PyInstaller...
echo      Please wait...
echo.

python -m PyInstaller --noconfirm --onefile --windowed --name "TSTC_Professional_PDF_Suite" --clean %ICON_ARG% %DATA_ARG% --hidden-import=customtkinter --hidden-import=pypdf --hidden-import=fitz --hidden-import=pymupdf --hidden-import=PIL --hidden-import=pdf2docx --hidden-import=docx --hidden-import=pytesseract --hidden-import=requests --hidden-import=urllib3 --collect-all customtkinter --collect-all pypdf --collect-all pymupdf --collect-all PIL --collect-all pdf2docx --collect-all docx "App.py"

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [4/4] Checking for Inno Setup Compiler to build installer...
set "ISCC="
if exist "C:\Program Files\Inno Setup 7\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC (
    echo      Compiling Windows Setup Installer with Inno Setup...
    "%ISCC%" "TSTC_Professional PDF Suite.iss"
    if errorlevel 1 (
        echo [WARNING] Inno Setup compilation encountered an issue.
    ) else (
        echo      Installer created at: %~dp0Output\TSTC_Professional_PDF_Suite_Setup.exe
    )
) else (
    echo      [INFO] Inno Setup compiler not found; skipped setup.exe compilation.
)

echo.
echo  ================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo  ================================================
echo.
echo  Portable Executable:
echo      %~dp0dist\TSTC_Professional_PDF_Suite.exe
if exist "%~dp0Output\TSTC_Professional_PDF_Suite_Setup.exe" (
    echo.
    echo  Setup Installer:
    echo      %~dp0Output\TSTC_Professional_PDF_Suite_Setup.exe
)
echo.
pause
