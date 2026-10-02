@echo off
setlocal
cd /d "%~dp0"
set "TARGET=..\Dream_Data\resources.assets"
set "BACKUP=..\Dream_Data\resources.assets.orig"
set "DLL=..\Dream_Data\Managed\Assembly-CSharp-firstpass.dll"
set "DLLBAK=..\Dream_Data\Managed\Assembly-CSharp-firstpass.dll.orig"
if not exist "%TARGET%" ( echo Could not find %TARGET%. Put this folder inside the game folder. & pause & exit /b 1 )
if not exist "%BACKUP%" ( echo Backing up original resources.assets... & copy /y "%TARGET%" "%BACKUP%" >nul )
if not exist "%DLLBAK%" ( echo Backing up original Assembly-CSharp-firstpass.dll... & copy /y "%DLL%" "%DLLBAK%" >nul )
echo Applying retranslation patch...
xdelta3.exe -d -f -s "%BACKUP%" "Dream_patch.xdelta" "%TARGET%.new"
if errorlevel 1 ( echo. & echo Translation patch failed. Your game files were not changed. & del "%TARGET%.new" 2>nul & pause & exit /b 1 )
echo Applying save fix...
xdelta3.exe -d -f -s "%DLLBAK%" "SaveFix_firstpass.xdelta" "%DLL%.new"
if errorlevel 1 ( echo. & echo Save fix failed. Your game files were not changed. & del "%TARGET%.new" "%DLL%.new" 2>nul & pause & exit /b 1 )
move /y "%TARGET%.new" "%TARGET%" >nul
move /y "%DLL%.new" "%DLL%" >nul
echo Done! Start the game with the language set to English.
pause
