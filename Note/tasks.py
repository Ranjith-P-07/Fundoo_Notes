from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Notes
from datetime import datetime, timedelta
from django_celery_results.models import TaskResult
import time

@shared_task()
def delete_trashed_note():
    notes = Notes.objects.filter(is_trashed=True)
    for note in notes:
        if datetime.now() - note.trashed_time.replace(tzinfo=None) > timedelta(days=7):
            note.delete()
    return "Trashed Note is deleted"

@shared_task()
def note_reminder():
    notes = Notes.objects.filter(is_trashed=False).exclude(reminder=None)
    print(datetime.now())
    for note in notes:
        if note.reminder.replace(tzinfo=None) - datetime.now() <= timedelta(minutes=1):
            print(note.reminder)
            note.reminder = None
            note.save()
            return "Reminder has been Triggered..!!!"