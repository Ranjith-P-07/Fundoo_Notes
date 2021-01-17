import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fundoo.settings')

app = Celery('Fundoo')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'Check Every Day':{
        'task':'Note.tasks.delete_trashed_note',
        'schedule':10,
    }
}

app.autodiscover_tasks()



@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')