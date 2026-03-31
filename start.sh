#!/bin/bash
set -e

echo "==> Lancement des migrations..."
python manage.py migrate --noinput

echo "==> Démarrage de Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
