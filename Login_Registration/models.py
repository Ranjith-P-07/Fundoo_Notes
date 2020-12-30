from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from PIL import Image


class Registration(models.Model):
    username = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=True)
    password1 = models.CharField(max_length=60)
    password2 = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='defaultimage.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'