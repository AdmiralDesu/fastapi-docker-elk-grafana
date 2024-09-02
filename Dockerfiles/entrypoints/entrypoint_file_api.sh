#!/usr/bin/env sh

/opt/app/.venv/bin/alembic -c /opt/app/alembic.ini upgrade head &
exec /opt/app/.venv/bin/python /opt/app/run.py