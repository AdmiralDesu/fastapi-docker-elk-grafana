#!/usr/bin/env sh

exec /opt/app/.venv/bin/celery -A worker.celery worker -n file_api_worker -f ./logs/celery.log -c 15 -E