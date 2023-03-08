#!/bin/sh

set -e

SETUP_MODE=BUILD /venv/bin/python manage.py migrate

exec "$@"
