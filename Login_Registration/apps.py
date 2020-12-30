from django.apps import AppConfig


class LoginRegistrationConfig(AppConfig):
    name = 'Login_Registration'


    def ready(self):
        import Login_Registration.signals
