#!/bin/sh
set -e

echo "Applying database migrations..."
cp configs.example.py configs.py
python manage.py makemigrations
python manage.py migrate

WORKERS=${WORKERS:-4}
THREADS=${THREADS:-4}
TIMEOUT=${TIMEOUT:-600}

echo "Starting Qexo with ${WORKERS} workers, ${THREADS} threads, and ${TIMEOUT}s timeout..."

exec gunicorn -b 0.0.0.0:8000 core.wsgi:application \
    --workers=$WORKERS --threads=$THREADS --timeout=$TIMEOUT
