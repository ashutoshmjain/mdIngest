@echo off
cd /d "%~dp0"
title md² Ingest Publishing Cockpit
echo ==================================================
echo       md² Ingest Publishing Cockpit Launcher
echo ==================================================
echo.
echo Launching the md² Publishing Cockpit Server...
echo.
where py >nul 2>nul
if not errorlevel 1 (
    set PYLAUNCH=py -3
) else (
    set PYLAUNCH=python
)
if exist "ingest\server.py" (
    %PYLAUNCH% ingest\server.py
)
echo.
echo Server has stopped.
pause
