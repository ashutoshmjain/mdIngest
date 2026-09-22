@echo off
cd /d "%~dp0"
title md² Ingest Publishing Cockpit
echo ==================================================
echo       md² Ingest Publishing Cockpit Launcher
echo ==================================================
echo.
echo Launching the md² Publishing Cockpit Server...
echo.
if exist "ingest\server.py" (
    python ingest\server.py
) else if exist "ui\server.py" (
    python ui\server.py
)
echo.
echo Server has stopped.
pause
