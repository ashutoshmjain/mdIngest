@echo off
cd /d "%~dp0"
title DDMA Clip Curator Server
echo ==================================================
echo       DDMA Clip Curator Server Launcher
echo ==================================================
echo.
echo Launching the DDMA Clip Curator Server...
echo.
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 scratch/run_curator.py
) else (
    python scratch/run_curator.py
)
echo.
echo Server has stopped.
pause
