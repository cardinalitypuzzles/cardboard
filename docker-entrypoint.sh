#!/bin/sh

# Compiles the js bundle(s) and runs in background to hot reload
yarn run dev &

python manage.py migrate

# Password is burrito (in docker-compose.yaml)
python manage.py createsuperuser --noinput --username admin --email cardinalitypuzzles@gmail.com

exec "$@"
