#!/bin/sh
set -e

# Export once before migrations and before Gunicorn forks its workers.
if [ -z "${DJANGO_SECRET_KEY:-}" ] && [ -z "${VERCEL:-}" ]; then
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(64))')
    export DJANGO_SECRET_KEY
fi

echo "Applying database migrations..."
cp configs.example.py configs.py
python manage.py makemigrations
python manage.py migrate --noinput

WORKERS=${WORKERS:-4}
THREADS=${THREADS:-4}
TIMEOUT=${TIMEOUT:-600}

echo "Starting Qexo with ${WORKERS} workers, ${THREADS} threads, and ${TIMEOUT}s timeout..."

exec gunicorn -b 0.0.0.0:8000 core.wsgi:application \
    --workers=$WORKERS --threads=$THREADS --timeout=$TIMEOUT
