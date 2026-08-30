@echo off
cd /d "%~dp0"
title mdBook Serve (Local Preview)
echo ==================================================
echo       mdBook Live Preview Server (Port 3000)
echo ==================================================
echo.
echo Starting mdbook serve on http://localhost:3000 and http://127.0.0.1:3000 ...
echo.
mdbook serve --hostname 0.0.0.0 -p 3000
echo.
echo mdBook server stopped.
pause
