release: python manage.py migrate --noinput
web: daphne smallboard.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: celery -A smallboard worker -l INFO --without-heartbeat --without-gossip --without-mingle
bot: python manage.py rundiscordbot
channel_worker: python manage.py runworker --only-channels=http.* --only-channels=websocket.* -v2