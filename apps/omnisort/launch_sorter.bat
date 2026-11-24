@echo off
title Titus OmniSort Pro - Folder & File Sorter 2-in-1 Utility
echo Starting Titus OmniSort Pro...
start "" pythonw run_sorter.py
if %ERRORLEVEL% NEQ 0 (
    echo Pythonw launch failed, trying standard python...
    python run_sorter.py
)

