from django.urls import path, include
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.Registration.as_view(), name='register'),
    path('activate/<surl>/', views.activate, name="activate"),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('forgotpassword/', views.Forgotpassword.as_view(), name="forgotpassword"),
    path('reset_password/<surl>/', views.reset_password, name="reset_password"),
    path('resetpassword/<user_reset>/', views.ResetPassword.as_view(), name="resetpassword"),
]