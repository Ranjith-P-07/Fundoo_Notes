from django.urls import path, include
from .views import NoteCreateView
from . import views

urlpatterns = [
    path('note/', views.NoteCreateView.as_view() ,name='create_note'),
    path('list/', views.ListNoteView.as_view(), name='note-list'),
]