@echo off
title Compilation de BulkFolder
echo ==========================================
echo    PREPARATION DE LA COMPILATION
echo ==========================================
echo.

echo 1. Nettoyage des anciens fichiers de build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "BulkFolder.spec" del "BulkFolder.spec"

echo.
echo 2. Lancement de PyInstaller...
echo Cela peut prendre une ou deux minutes, patience !
echo.

REM Explication des parametres :
REM --noconfirm : Ecrase le dossier dist/ sans demander la permission
REM --windowed  : Cache la console noire de Python au lancement (mode interface graphique pure)
REM --name      : Le nom de votre application
REM --icon      : L'icone de votre application (.ico)
REM --add-data  : Inclut votre dossier assets dans le .exe (le ";" est obligatoire sur Windows)
REM --paths     : Indique a PyInstaller ou trouver vos modules (le dossier src)
REM --collect-all customtkinter : Force l'inclusion des couleurs et themes de CustomTkinter

pyinstaller --noconfirm ^
    --windowed ^
    --name "BulkFolder" ^
    --icon="assets/logo.ico" ^
    --add-data "assets;assets" ^
    --paths="src" ^
    --collect-all customtkinter ^
    "src/bulkfolder/ui/main.py"

echo.
echo ==========================================
echo    COMPILATION TERMINEE AVEC SUCCES !
echo ==========================================
echo.
echo Vous trouverez votre application BulkFolder dans le dossier "dist\BulkFolder".
echo.
pause
