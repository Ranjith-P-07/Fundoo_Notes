from rest_framework import serializers
from .models import Notes, Label
from django.contrib.auth.models import User
    
class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'is_archive', 'is_trashed', 'is_pinned', 'color', 'label']

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['labelname']