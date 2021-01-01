from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from colorful.fields import RGBColorField

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    is_archive = models.BooleanField("is_archive", default=False)
    is_trashed = models.BooleanField("is_trashed", default=False)
    is_pinned = models.BooleanField(default=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    color = RGBColorField(colors=['#FF0000', '#00FF00', '#0000FF'], blank=True, null=True)

    def __str__(self):
        return str(self.user)
