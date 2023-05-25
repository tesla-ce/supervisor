#!/bin/sh

set -e

if [ ! -f $POSTGRES_PASSWORD_FILE ]; then
  cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' > $POSTGRES_PASSWORD_FILE
fi

if [ "$SETUP_MODE" != 'SETUP' ]; then
  /bin/postgres_docker-entrypoint.sh postgres &
  /bin/wait_for_it.sh "localhost:5432" -- echo "Database is up"
  SETUP_MODE=BUILD /venv/bin/python manage.py migrate
fi
exec "$@"
