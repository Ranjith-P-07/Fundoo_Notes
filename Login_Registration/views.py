from django.shortcuts import render, redirect

from rest_framework.generics import GenericAPIView
from .serializers import RegistrationSerializers, LoginSerializers
from rest_framework.response import Response
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, get_user_model

from rest_framework_jwt.settings import api_settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

from django_short_url.views import get_surl
from django_short_url.models import ShortURL

from django.template.loader import render_to_string, get_template
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth import login, logout
from rest_framework import authentication, permissions

import jwt
from Fundoo import settings

from django.views.generic import TemplateView
User = get_user_model()

def home(request):
    return render(request, 'home.html')
    


class Registration(GenericAPIView):
    serializer_class = RegistrationSerializers
    # def get(self, request):
    #     return render(request,'registration.html')
    
    def post(self, request):
        if request.user.is_authenticated:
            return Response("your are already registred,please do login")
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')
        print(password1)
        if len(password1) < 4 or len(password2) <4:
            return Response("length of the password must be greater than 4") 
        elif password1 != password2:
            return Response("passwords are not matching")
        check_name = User.objects.filter(
            Q(username__iexact=username)
        )
        check_email = User.objects.filter(
            Q(email__iexact=email)
        )
        if check_name.exists():
            return Response("already user id present with this username ")
        elif check_email.exists():
            return Response("already user id present with this  email")
        else:
            user = User.objects.create(username=username, email=email)
            user.set_password(password1)
            user.is_active = False
            user.save()
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # user is unique then we will send token to his/her email for validation
            # token = token_activation(user.username, user.password)
            url = str(token)
            surl = get_surl(url)
            z = surl.split("/")
            mail_subject = "Activate your account by clicking below link"
            mail_message = render_to_string('email_validation.html', {
                'user': user.username,
                'domain': get_current_site(request).domain,
                'surl': z[2]
            })
            recipient_email = user.email
            subject, from_email, to = 'greeting from fundoo,Activate your account by clicking below link', settings.EMAIL_HOST, recipient_email
            msg = EmailMultiAlternatives(subject, mail_message, from_email, [to])
            msg.attach_alternative(mail_message, "text/html")
            msg.send()
            return Response({"details": "verify through your email"})


def activate(request, surl):
    try:
        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, settings.SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)
        # if user is not none then user account willed be activated
        if user is not None:
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return Response('not valid user')
    except KeyError as e:
        return Response(e)
    except Exception as f:
        return Response(f)



