@echo off
cd /d "%~dp0"
title md² Ingest Publishing Cockpit
echo ==================================================
echo       md² Ingest Publishing Cockpit Launcher
echo ==================================================
echo.
echo Launching the md² Publishing Cockpit Server...
echo.
python ingest/server.py
echo.
echo Server has stopped.
pause
