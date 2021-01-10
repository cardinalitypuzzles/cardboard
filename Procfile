release: python manage.py migrate --noinput
web: gunicorn smallboard.wsgi --log-file -

cgs_worker1: celery -A smallboard worker -l INFO -Q cgs_queue
cgs_worker2: celery -A smallboard worker -l INFO -Q cgs_queue
cgs_worker3: celery -A smallboard worker -l INFO -Q cgs_queue

worker: celery -A smallboard worker -l INFO
