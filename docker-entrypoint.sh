#!/bin/sh

yarn install
yarn run dev

python manage.py migrate
python manage.py collectstatic --no-input

# Password is burrito (in docker-compose.yaml)
python manage.py createsuperuser --noinput --username admin --email cardinalitypuzzles@gmail.com

exec "$@"
