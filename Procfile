release: python manage.py migrate --noinput
web: gunicorn smallboard.wsgi --log-file -
worker: celery -A smallboard worker -l INFO
