@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "files\install.ps1"
echo.
pause
