release: python manage.py migrate --noinput
web: gunicorn smallboard.wsgi --log-file -
worker: celery -A smallboard worker -l INFO --without-heartbeat --without-gossip --without-mingle
bot: python manage.py rundiscordbot
