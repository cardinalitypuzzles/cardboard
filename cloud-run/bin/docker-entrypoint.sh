#!/bin/sh
set -e

echo "Activating venv"
. /venv/bin/activate

case "$1" in
    web)
        echo "Running migrate..."
        python manage.py migrate
        ;;
    celery)
        ;;
    bot)
        ;;
    *)
        echo "ERROR: Invalid container name: $1"
        exit 1
        ;;
esac

shift 1

echo "Running CMD..."
exec "$@"
