@echo off
cd /d "%~dp0"
if not exist "..\Dream_Data\resources.assets.orig" ( echo No backup found - nothing to restore. & pause & exit /b 1 )
copy /y "..\Dream_Data\resources.assets.orig" "..\Dream_Data\resources.assets" >nul
if exist "..\Dream_Data\Managed\Assembly-CSharp-firstpass.dll.orig" copy /y "..\Dream_Data\Managed\Assembly-CSharp-firstpass.dll.orig" "..\Dream_Data\Managed\Assembly-CSharp-firstpass.dll" >nul
echo Original game files restored.
pause
