#!/bin/sh

set -e

/venv/bin/python manage.py migrate

exec "$@"
