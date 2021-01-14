release: python manage.py migrate --noinput
web: daphne smallboard.asgi:django_asgi_app --port $PORT --bind 0.0.0.0 -v2
worker: celery -A smallboard worker -l INFO --without-heartbeat --without-gossip --without-mingle
bot: python manage.py rundiscordbot
channel: python manage.py runworker channel_layer -v2
