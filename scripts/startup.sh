#!/bin/bash
# [STUDENT-ID: C4055929 - Ramanjaneyulu Reddy Avuduri] Azure App Service startup script

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Start Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 registrationApp.wsgi:application
