#!/bin/sh

yarn run dev &
python manage.py migrate
python manage.py collectstatic --no-input --clear

exec "$@"
