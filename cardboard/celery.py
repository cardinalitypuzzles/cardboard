import os

import dotenv
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cardboard.settings")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

app = Celery("cardboard")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# single worker queue for querying drive activity
app.conf.task_routes = {
    "google_api_lib.tasks.update_active_users": {"queue": "activity_updates_queue"}
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
