release: python manage.py migrate --noinput
web: gunicorn cardboard.wsgi --log-file -
worker: celery -A cardboard worker -l INFO --without-heartbeat --without-gossip --without-mingle --concurrency 2
worker: celery -A cardboard worker -l INFO --without-heartbeat --without-gossip --without-mingle --concurrency 1 -Q activity_updates_queue --beat
bot: python manage.py rundiscordbot
