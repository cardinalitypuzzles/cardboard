#!/bin/sh

yarn install
yarn run dev

# Migrations run in their own compose service, before this container starts.
python manage.py collectstatic --no-input

# Password is burrito (in docker-compose.yaml)
python manage.py createsuperuser --noinput --username admin --email cardinalitypuzzles@gmail.com

exec "$@"
