from django.shortcuts import render, redirect

from rest_framework.generics import GenericAPIView
from .serializers import RegistrationSerializers, LoginSerializers, EmailSerializers, ResetSerializers, ProfileUpdateSerializer
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

from django.contrib.auth.decorators import login_required
from rest_framework import permissions
from .models import Profile

from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator

import logging
from Fundoo.settings import file_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

@login_required(login_url='login')
def home(request):
    """
    Summary:
    --------
        This is a simple Home page.
    """
    logger.info("User logged into home page")
    return render(request, 'home.html')
    


class Registration(GenericAPIView):
    serializer_class = RegistrationSerializers

    @swagger_auto_schema(responses={200: RegistrationSerializers()})
    
    def post(self, request):
        """
        This api is for user registration to this application

        @param request: user registration data like username, email and  password
        @return: account verification link to registered email once registration is successful
        """
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')
        if len(password1) < 4 or len(password2) <4:
            logger.error("length of the password must be greater than 4, from post()")
            return Response("length of the password must be greater than 4", status=status.HTTP_400_BAD_REQUEST)
        elif password1 != password2:
            logger.error("passwords are not matching, from post()")
            return Response("passwords are not matching", status=status.HTTP_400_BAD_REQUEST)
        check_name = User.objects.filter(
            Q(username__iexact=username)
        )
        check_email = User.objects.filter(
            Q(email__iexact=email)
        )
        if check_name.exists():
            logger.error("already user id present with this username, from post()")
            return Response("already user id present with this username ")
        elif check_email.exists():
            logger.error("already user id present with this  email, from post()")
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
            short_token = surl.split("/")
            mail_subject = "Activate your account by clicking below link"
            mail_message = render_to_string('email_validation.html', {
                'user': user.username,
                'domain': get_current_site(request).domain,
                'surl': short_token[2]
            })
            recipient_email = user.email
            subject, from_email, to = 'greeting from fundoo,Activate your account by clicking below link', settings.EMAIL_HOST, recipient_email
            msg = EmailMultiAlternatives(subject, mail_message, from_email, [to])
            msg.attach_alternative(mail_message, "text/html")
            msg.send()
            logger.info("verify through your email, from post()")
            return Response({"details": "verify through your email"}, status=status.HTTP_201_CREATED)

def activate(request, surl):
    """
        @param request: once the account verification link is clicked by user this will take that request
        @return: it will redirect to login page
    """
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
            logger.info("redirecting to login page, from activate method")
            return redirect('login')
        else:
            logger.error("not a valid user, from activate method")
            return Response('not valid user')
    except KeyError as e:
        return Response(e)
    except Exception as f:
        return Response(f)

class Login(GenericAPIView):
    serializer_class = LoginSerializers
    permission_classes = (AllowAny,)


    def post(self, request):
        """
        This API is used to authenticate user to access resources
        @param request: user credential like username and password
        @return: Redirects to my basic home page
        """
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        try:
            check = User.objects.filter(
                Q(username__iexact=username) or
                Q(email__iexact=email)
            )
            if check.count() == 1:
                user_obj = check.first()
                if user_obj.check_password(password):
                    user = user_obj
                    login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    # return redirect('/auth/home', status=status.HTTP_200_OK)
                    logger.info("Login successful, from post()")
                    return Response({"response": "Login successful"}, status=status.HTTP_200_OK)
                logger.error("check password again")
                return Response("check password again", status=status.HTTP_403_FORBIDDEN)
            logger.error("multiple users are present with this username")
            return Response("multiple users are present with this username", status=status.HTTP_403_FORBIDDEN)
        except:
            logger.error("No User Exist with this username or email")
            return Response("No User Exist with this username or email", status=status.HTTP_403_FORBIDDEN)

@method_decorator(login_required(login_url='/Login/login/'), name='dispatch')
class Logout(GenericAPIView):
    """
        This api is for user log out
        @return: release all resources from user on logged out
    """
    serializer_class = LoginSerializers
    def get(self, request):
        try:
            user = request.user
            logout(request)
            logger.info('your succefully logged out,thankyou')
            return Response({'details': 'your succefully logged out,thankyou'}, status=status.HTTP_200_OK)
        except Exception:
            logger.error('something went wrong while logout')
            return Response({'details': 'something went wrong while logout'}, status=status.HTTP_403_FORBIDDEN)

        

class Forgotpassword(GenericAPIView):

    serializer_class = EmailSerializers

    def post(self, request):
        """
            This api is used to send reset password request to server
            @param request: user registered email id
            @return: sends a password reset link to user validated email id
        """
        email = request.data['email']
        if email == "":
            logger.error('email should not be empty')
            return Response({'details': 'email should not be empty'})
        else:
            try:
                validate_email(email)
            except Exception:
                logger.error('not a valid email')
                return Response({'details': 'not a valid email'})
            try:
                user = User.objects.filter(email=email)
                user_email = user.values()[0]['email']
                user_username = user.values()[0]['username']
                user_id = user.values()[0]['id']
                if user_email:
                    token = token_activation(user_username, user_id)
                    url = str(token)
                    surl = get_surl(url)
                    short_token = surl.split('/')
                    mail_subject = "Activate your account by clicking below link"
                    mail_message = render_to_string('email_validate.html', {
                        'user': user_username,
                        'domain': get_current_site(request).domain,
                        'surl': short_token[2]
                    })
                    recipient_email = user_email
                    subject, from_email, to = 'greeting from fundoo,Activate your account by clicking below link', settings.EMAIL_HOST, recipient_email
                    msg = EmailMultiAlternatives(subject, mail_message, from_email, [to])
                    msg.attach_alternative(mail_message, "text/html")
                    msg.send()
                    logger.info('please check your email,link has sent your email, from forgotpassword')
                    return Response({'details': 'please check your email,link has sent your email'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error('something went wrong')
                return Response({'details': 'something went wrong'})
   
def reset_password(request, surl):
    """
        This api is used to Decode that jwt token and redirect to Resetpassword API
    """
    try:
        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, settings.SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)

        # if user is not none then we will fetch the data and redirect to the reset password page
        if user is not None:
            context = {'userReset': user.username}
            return redirect('/auth/resetpassword/' + str(user)+'/')
        else:
            messages.info(request, 'was not able to sent the email')
            return redirect('forgotpassword')
    except KeyError:
        logger.error("was not able to sent the email")
        messages.info(request, 'was not able to sent the email')
        return redirect('forgotpassword')
    except Exception as e:
        messages.info(request, 'activation link expired')
        return redirect('forgotpassword')


class ResetPassword(GenericAPIView):
    serializer_class = ResetSerializers

    def post(self, request, user_reset):
        """
            This API is used to reset user password
            @param: user id and decoded token fetched for resetpassword request
            @return: reset user password
        """
        password1 = request.data['password']

        if user_reset is None:
            logger.error('not a valid user')
            return Response({'details': 'not a valid user'})
        elif (password1) == "":
            logger.error('password should not be empty')
            return Response({'details': 'password should not be empty'})
        else:
            try:
                user = User.objects.get(username=user_reset)
                user.set_password(password1)
                user.save()
                logger.info('your password has been Set')
                return Response({'details': 'your password has been Set'})
            except Exception:
                logger.error('not a valid user')
                return Response({'details': 'not a valid user'})

class ProfileUpdate(GenericAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
            This API is used to update user profile
            @param: user profile data
            @return: updates user profile
        """
        img = request.FILES['image']
        try:
            user = Profile.objects.get(user=request.user)
            serializer = ProfileUpdateSerializer(user, data={'image':img})

            if serializer.is_valid():
                serializer.save()
                logger.info('Profile image updated')
                return Response('Profile image updated', status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=400)
        except:
            return Response(serializer.errors, status=400)

    

