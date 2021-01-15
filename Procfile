release: python manage.py migrate --noinput
web: daphne smallboard.routing:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A smallboard worker -l INFO --without-heartbeat --without-gossip --without-mingle
bot: python manage.py rundiscordbot
