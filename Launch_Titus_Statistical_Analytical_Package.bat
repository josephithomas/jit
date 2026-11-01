@echo off
title Titus Statistical Analytical Package - Titus II Teachers College Thiruvalla
cls
echo =========================================================================
echo   Starting Titus Statistical Analytical Package (TSAP)
echo   Titus II Teachers College, Thiruvalla
echo   100 Advanced Statistical Tests (SPSS/Jamovi) + Qualitative AI (NVivo/MAXQDA)
echo =========================================================================
echo.

cd /d "%~dp0"
python server.py
pause
