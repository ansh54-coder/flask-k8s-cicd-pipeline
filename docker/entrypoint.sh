#!/bin/sh

set -e

echo "Running database migrations..."

flask --app app.main db upgrade

echo "Starting ShopAPI..."

exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    "app.main:app"
