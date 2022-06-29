import os

from celery import Celery

# Set the default settings module fro celery.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aria.settings")

# Avoid having to always pass settings module for celery.
app = Celery("aria")

# Tell celery to use django settings for config, instead of own config file.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
