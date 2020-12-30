from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# class Label(models.Model):
#     labelname = models.CharField(max_length=100)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.labelname


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    # label = models.ManyToManyField(Label, max_length=100)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_archive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
