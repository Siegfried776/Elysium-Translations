@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "files\uninstall.ps1"
echo.
pause
