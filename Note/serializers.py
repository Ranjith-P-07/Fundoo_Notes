from rest_framework import serializers
from .models import Notes, Label
from django.contrib.auth.models import User
from datetime import datetime, timedelta
    
class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'is_archive', 'is_trashed', 'is_pinned', 'color', 'label', 'collabrator']
        extra_kwargs = {'label': {'read_only': True}, 'collabrator': {'read_only': True}, 'color': {'read_only': True}}

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['labelname']

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['reminder']
    def validate_reminder(self, time):
        if time.replace(tzinfo=None) - datetime.now() < timedelta(seconds=0):
            raise serializers.ValidationError("Invaild reminder, Check your reminder once again..!!")
        return time