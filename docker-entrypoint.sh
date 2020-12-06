#!/bin/sh

# Compiles the js bundle(s) and runs in background to hot reload
yarn run dev &

python manage.py migrate

exec "$@"
