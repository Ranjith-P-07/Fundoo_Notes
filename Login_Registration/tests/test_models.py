from django.test import TestCase
from ..models import Registration, Profile

class RegistrationTest(TestCase):
    """ Test module for Registration model """
    def setUp(self):
        Registration.objects.create(
            username='Ranjith', email='ranjith@gmail.com', password1='123456r', password2='123456r')
        Registration.objects.create(
            username='Rahul', email='rahul@gmail.com', password1='123456', password2='123456'
        )
    

    def test_registeration_username(self):
        registration_Ranjith = Registration.objects.get(username='Ranjith')
        registration_Rahul = Registration.objects.get(username='Rahul')
        self.assertEqual(registration_Ranjith.get_username(), "Ranjith")
        self.assertEqual(registration_Rahul.get_username(), "Rahul")

    def test_registeration_email(self):
        registration_Ranjith_email = Registration.objects.get(username='Ranjith')
        registration_Rahul_email = Registration.objects.get(username='Rahul')
        self.assertEqual(registration_Ranjith_email.get_email(), "ranjith@gmail.com")
        self.assertEqual(registration_Rahul_email.get_email(), "rahul@gmail.com")