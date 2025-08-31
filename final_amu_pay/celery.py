# your_project/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "final_amu_pay.settings")
app = Celery("final_amu_pay")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
