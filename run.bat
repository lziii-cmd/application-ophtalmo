@echo off
title Clinique Ophtalmologique - Serveur Local
color 0B

echo ============================================
echo   Clinique Ophtalmologique - Demarrage
echo ============================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [AVERTISSEMENT] Fichier .env introuvable. Copie depuis .env.example...
    copy .env.example .env
    echo [INFO] Veuillez editer le fichier .env avec vos parametres.
    echo.
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
) else (
    echo [AVERTISSEMENT] Environnement virtuel non trouve. Utilisation de Python systeme.
)

REM Create data directory if needed
if not exist "data" mkdir data

REM Apply migrations
echo [INFO] Application des migrations...
python manage.py migrate --run-syncdb

REM Collect static files
echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput 2>nul

echo.
echo ============================================
echo   Serveur demarre sur http://localhost:8000
echo   Appuyez sur CTRL+C pour arreter
echo ============================================
echo.

REM Start server
python manage.py runserver 127.0.0.1:8000

pause
