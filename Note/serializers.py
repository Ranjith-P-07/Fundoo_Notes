from rest_framework import serializers
from .models import Notes
from django.contrib.auth.models import User

# class LabelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Label
#         fields = '__all__'
    
class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'