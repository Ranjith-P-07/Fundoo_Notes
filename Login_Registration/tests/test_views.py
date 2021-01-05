from django.test import TestCase, Client
from rest_framework import status
from django.urls import reverse
from ..models import Registration
from ..serializers import RegistrationSerializers
import json

client = Client()

class AuthenticationAPITest(TestCase):

    def setUp(self):
        user = Registration.objects.create(username='Rahul', email='Rahul@gmail.com', password1='123456r', password2='123456r')

        self.valid_payload = {
            'username': 'Rahul',
            'email': 'Rahul@gmail.com',
            'password1': '123456r',
            'password2': '123456r',
        }

        self.invalid_payload1 = {
            'username': 'Rahul',
            'email': 'Rahul@gmail.com',
            'password1': '123',
            'password2': '123',
        }

        self.invalid_payload2 = {
            'username': 'Rahul',
            'email': 'Rahul@gmail.com',
            'password1': '123456r',
            'password2': '1234',
        }

        self.valid_credentials = {
            'username': 'Rahul',
            'password': '123456r',
        }

        self.invalid_credentials = {
            'username': 'r',
            'password': '123456r',
        }

        self.valid_credentials1= {
            'email' : 'Rahul@gmail.com',
        }

    def test_register_user_with_valid_payload(self):
        response = client.post(reverse('register'),data=json.dumps(self.valid_payload), content_type='application/json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_with_invalid_password_length(self):
        response = client.post(reverse('register'),data=json.dumps(self.invalid_payload1), content_type='application/json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_invalid_password_match(self):
        response = client.post(reverse('register'),data=json.dumps(self.invalid_payload2), content_type='application/json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_valid_credentials(self):
        response = client.post(reverse('login'), data=json.dumps(self.valid_credentials), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_invalid_credentials(self):
        response = client.post(reverse('login'), data=json.dumps(self.invalid_credentials), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_logout(self):
        client.post(reverse('login'), data=json.dumps(self.valid_credentials), content_type='application/json')
        response = client.get(reverse('logout'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forgotPass(self):
        client.post(reverse('login'), data=json.dumps(self.valid_credentials), content_type='application/json')
        response = client.post(reverse('forgotpassword'), data=json.dumps(self.valid_credentials1), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


