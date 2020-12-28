from django.shortcuts import render, redirect

from rest_framework.generics import GenericAPIView
from .serializers import RegistrationSerializers, LoginSerializers, EmailSerializers, ResetSerializers
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

from django.core.validators import validate_email
from .token import token_activation
from django.contrib import messages

from drf_yasg.utils import swagger_auto_schema

def home(request):
    return render(request, 'home.html')
    


class Registration(GenericAPIView):
    serializer_class = RegistrationSerializers
    # def get(self, request):
    #     return render(request,'registration.html')

    @swagger_auto_schema(responses={200: RegistrationSerializers()})
    
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

class Login(GenericAPIView):
    serializer_class = LoginSerializers

    # def get(self, request):
    #     return render(request, 'login.html')


    def post(self, request):
        if request.user.is_authenticated :
            return Response({'details': 'user is already authenticated'})
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        print(username, password)
        try:
            qs = User.objects.filter(
                Q(username__iexact=username) or
                Q(email__iexact=email)
            )
            if qs.count() == 1:
                user_obj = qs.first()
                if user_obj.check_password(password):
                    user = user_obj
                    login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    return redirect('/auth/home')
                return Response("check password again")
            return Response("multiple users are present with this username")
        except:
            return Response("No User Exist with this username or email")


class Logout(GenericAPIView):
    serializer_class = LoginSerializers
    def get(self, request):
        try:
            user = request.user
            logout(request)
            return Response({'details': 'your succefully loggeg out,thankyou'})
        except Exception:
            return Response({'details': 'something went wrong while logout'})

        

class Forgotpassword(GenericAPIView):

    serializer_class = EmailSerializers

    def post(self, request):
        # data = request.data
        email = request.data['email']
        if email == "":
            return Response({'details': 'email should not be empty'})
        else:
            try:
                validate_email(email)
            except Exception:
                return Response({'details': 'not a valid email'})
            try:
                user = User.objects.filter(email=email)
                user_email = user.values()[0]['email']
                user_username = user.values()[0]['username']
                user_id = user.values()[0]['id']
                # print(user_email, user_id, user_username)
                if user_email:
                    token = token_activation(user_username, user_id)
                    print(token)
                    # payload = jwt_payload_handler(user_username)
                    # token = jwt_encode_handler(payload)
                    url = str(token)
                    surl = get_surl(url)
                    z = surl.split('/')
                    # print(z)
                    mail_subject = "Activate your account by clicking below link"
                    print(user_username, get_current_site(request).domain)
                    mail_message = render_to_string('email_validate.html', {
                        'user': user_username,
                        'domain': get_current_site(request).domain,
                        'surl': z[2]
                    })
                    # print(mail_message)
                    recipient_email = user_email
                    subject, from_email, to = 'greeting from fundoo,Activate your account by clicking below link', settings.EMAIL_HOST, recipient_email
                    msg = EmailMultiAlternatives(subject, mail_message, from_email, [to])
                    # print(msg)
                    msg.attach_alternative(mail_message, "text/html")
                    msg.send()
                    return Response({'details': 'please check your email,link has sent your email'})
            except:
                return Response({'details': 'something went wrong'})
    
def reset_password(request, surl):
    try:
        # here decode is done with jwt

        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, settings.SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)

        # if user is not none then we will fetch the data and redirect to the reset password page
        if user is not None:
            context = {'userReset': user.username}
            print(context)
            return redirect('/auth/resetpassword/' + str(user)+'/')
        else:
            messages.info(request, 'was not able to sent the email')
            return redirect('forgotpassword')
    except KeyError:
        messages.info(request, 'was not able to sent the email')
        return redirect('forgotpassword')
    except Exception as e:
        print(e)
        messages.info(request, 'activation link expired')
        return redirect('forgotpassword')


class ResetPassword(GenericAPIView):
    serializer_class = ResetSerializers

    def post(self, request, user_reset):
        password1 = request.data['password']

        if user_reset is None:
            return Response({'details': 'not a valid user'})
        elif (password1) == "":
            return Response({'details': 'password should not be empty'})
        else:
            try:
                user = User.objects.get(username=user_reset)
                user.set_password(password1)
                user.save()
                return Response({'details': 'your password has been Set'})
            except Exception:
                return Response({'details': 'not a valid user'})