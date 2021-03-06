from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from colorful.fields import RGBColorField


class Label(models.Model):
    labelname = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_labelname(self):
        return self.labelname

    def __str__(self):
        return self.labelname



class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    is_archive = models.BooleanField("is_archive", default=False)
    is_trashed = models.BooleanField("is_trashed", default=False)
    is_pinned = models.BooleanField(default=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    color = RGBColorField(colors=['#FF0000', '#00FF00', '#0000FF'], blank=True, null=True)
    label = models.ManyToManyField(Label, blank=True)
    collabrator = models.ManyToManyField(User, related_name="Collabrator_of_note", blank=True)
    trashed_time = models.DateTimeField(default=None, blank=True, null=True)
    reminder = models.DateTimeField(default=None, blank=True, null=True)

    def get_note(self):
        return self.note

    def __str__(self):
        return self.title
