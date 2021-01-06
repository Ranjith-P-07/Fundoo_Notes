from django.test import TestCase
from ..models import Label, Notes
from django.contrib.auth.models import User

class NotesTest(TestCase):
    """ Test module for Registration model """
    def setUp(self):
        self.user=User.objects.create(email='Rahul@gmail.com',username='Rahul',password='123456r')
        label = Label.objects.create(labelname='label 1', user=self.user)
        note = Notes.objects.create(user=self.user, title='First title', note='First note')
    
    def test_create_note(self):
        note = Notes.objects.get(title='First title')
        self.assertEqual(note.get_note(), "First note")

    def test_create_label(self):
        label = Label.objects.get(user=self.user)
        self.assertEqual(label.get_labelname(), "label 1")
    



