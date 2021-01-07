from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Label, Notes
from ..serializers import NotesSerializer, LabelSerializer
import json

class NoteViewAPITest(TestCase):
    """ Test module for notes view API's """

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username='Ram', email='dineshdevang011@gmail.com', password='pbkdf2_sha256$216000$wpomR1uhDsTl$D0YbscCIh/iE209f4G8fAoEXc059EInf1FILvDVOcrM=')
        self.user2 = User.objects.create(username='Rahul1', email='Rahul1@gmail.com', password='pbkdf2_sha256$216000$wpomR1uhDsTl$D0YbscCIh/iE209f4G8fAoEXc059EInf1FILvDVOcrM=')
        self.note_for_user1 = Notes.objects.create(title='title 1', note='note1', user=self.user1, is_archive=False, is_trashed=False, is_pinned=False)
        self.note_for_user2 = Notes.objects.create(title='title 2', note='note2', user=self.user2, is_archive=False, is_trashed=False, is_pinned=False)
        self.label_for_user1 = Label.objects.create(labelname='label1', user=self.user1)
        self.label_for_user2 = Label.objects.create(labelname='label2', user=self.user2)

                
        self.user1_credentials  = {
            "username": "Ram",
            "password":"12345678.ram"
        }

        self.valid_payload = {
            "title": "Test title",
            "note": "Test note"
        }

        self.invalid_payload = {
            "title": "Test title2",
            "note": ""
        }

        self.invalid_credentials = {
            'email':'ram@gmail.com',
            'password':'12345'
        }

        self.valid_label_payload = {
            "labelname": "Test Label"
        }

        self.invalid_label_payload = {
            "labelname": ""
        }

    def test_get_all_notes_without_login(self):
        notes = Notes.objects.filter(user=self.user1, is_archive=False, is_trashed=False, is_pinned=False)
        response = self.client.get(reverse('note-list'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_get_all_notes_if_login_with_invalid_credentials(self):
        self.client.post(reverse('login'),data=json.dumps(self.invalid_credentials),content_type='application/json')
        response = self.client.get(reverse('create_note'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
  
    def test_get_all_notes_after_login(self):
        self.client.post(reverse('login'),data=json.dumps(self.user1_credentials), content_type='application/json')
        notes = Notes.objects.filter(user=self.user1, is_archive=False, is_trashed=False, is_pinned=False)
        response = self.client.get(reverse('create_note'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_notes_of_with_is_archive_value_true_after_login(self):
        self.client.post(reverse('login'),data=json.dumps(self.user1_credentials), content_type='application/json')
        notes = Notes.objects.filter(user=self.user1, is_archive=True, is_trashed=False, is_pinned=False)
        serializer = NotesSerializer(notes, many=True)
        response = self.client.get(reverse('create_note'))
        self.assertNotEqual(response.data, serializer.data)

    def test_create_notes_with_valid_payload_without_login(self):
        response = self.client.post(reverse('create_note'),data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_create_notes_with_valid_payload_after_login(self):
        self.client.post(reverse('login'),data=json.dumps(self.user1_credentials), content_type='application/json')
        response = self.client.post(reverse('create_note'),data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notes_with_invalid_payload_after_login(self):
        self.client.post(reverse('login'), data=json.dumps(self.user1_credentials), content_type='application/json')
        response = self.client.post(reverse('create_note'), data=json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



