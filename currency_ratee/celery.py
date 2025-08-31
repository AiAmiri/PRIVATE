import os
from celery import Celery

# Use the project-level settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_amu_pay.settings')

# Use the project name for the Celery app to keep a single app instance
app = Celery('final_amu_pay')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
