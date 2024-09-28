#!/bin/bash
exec /opt/app/.venv/bin/alembic -c /opt/app/alembic.ini upgrade head & /opt/app/.venv/bin/python /opt/app/run.py