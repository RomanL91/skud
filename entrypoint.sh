#!/usr/bin/env sh

python manage.py migrate

# gunicorn --bind 0.0.0.0:8000 myproject.asgi -w 4 -k uvicorn.workers.UvicornWorker
uvicorn core.asgi:application --host 0.0.0.0 --port 8000