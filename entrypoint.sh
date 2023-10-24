#!/usr/bin/env sh

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --no-input
python -m celery --app core worker -l info &
python add_ssl_cert_script
python manage.py restart_HTTP_long_macroscope

# gunicorn --bind 0.0.0.0:8000 core.asgi -w 4 -k uvicorn.workers.UvicornWorker
uvicorn core.asgi:application --host 0.0.0.0 --port 8000
