from django.urls import path, include
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.Registration.as_view(), name='register'),
    path('activate/<surl>/', views.activate, name="activate"),
    path('login/', views.Login.as_view(), name='login'),
]