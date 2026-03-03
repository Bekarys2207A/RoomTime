from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomtime.settings")

app = Celery("roomtime")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {
"bookings.tasks.*": {"queue": "bookings"},
"notifications.tasks.*": {"queue": "notifications"},
}
app.conf.broker_connection_retry_on_startup = True
app.conf.task_default_retry_delay = 10
app.conf.task_annotations = {
    '*': {'max_retries': 3},
}
app.conf.result_backend_transport_options = {
    'visibility_timeout': 3600,
    "socket_timeout": 10,
}

app.conf.broker_transport_options = {
    "max_retries": 5,
    "interval_start": 0,
    "interval_step": 2,
    "interval_max": 10,
}

@app.task(name="core.health_check")
def health_check():
    return "Celery OK"