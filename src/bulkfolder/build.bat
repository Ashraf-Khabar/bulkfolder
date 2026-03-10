@echo off
title Compilation de BulkFolder
echo ==========================================
echo    PREPARATION DE LA COMPILATION
echo ==========================================

:: Cette ligne est cruciale : elle force le script à se placer à la racine du projet
cd /d "%~dp0\..\.."

echo 1. Nettoyage des anciens fichiers...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo 2. Lancement de PyInstaller avec le nouveau lanceur...
:: Nous utilisons run.py (le fichier créé à la racine) au lieu de main.py
python -m PyInstaller --noconfirm ^
    --windowed ^
    --name "BulkFolder" ^
    --icon="src/assets/logo.ico" ^
    --add-data "src/assets;assets" ^
    --paths="src" ^
    --collect-all customtkinter ^
    "run.py"

echo ==========================================
echo    COMPILATION TERMINEE AVEC SUCCES !
echo ==========================================
echo.
echo Vous trouverez votre application dans "dist\BulkFolder".
pause