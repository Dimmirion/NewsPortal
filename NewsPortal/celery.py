import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'weekly-newsletter': {
        'task': 'news.tasks.weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Каждый понедельник в 8:00
    },
}
app.conf.timezone = 'Europe/Moscow'