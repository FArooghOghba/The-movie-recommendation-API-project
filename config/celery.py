import os
from celery import Celery

from config.env import env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', env('DJANGO_SETTINGS_MODULE'))

celery = Celery('config')
celery.config_from_object('django.conf:django', namespace='CELERY')
celery.autodiscover_tasks()
