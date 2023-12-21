#!/bin/sh

yarn install
# Compiles the js bundle(s) and runs in background to hot reload
yarn run dev &

python manage.py migrate
python manage.py collectstatic

# Password is burrito (in docker-compose.yaml)
python manage.py createsuperuser --noinput --username admin --email cardinalitypuzzles@gmail.com

exec "$@"
