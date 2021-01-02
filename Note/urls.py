from django.urls import path
from .views import NoteCreateView, LabelCreateView, LabelUpdateView
from . import views

urlpatterns = [
    path('note/', views.NoteCreateView.as_view(), name='create_note'),
    path('list/', views.ListNoteView.as_view(), name='note-list'),
    path('noteupdate/<int:id>/', views.NoteUpdateView.as_view(), name='note-update'),
    path('label/', views.LabelCreateView.as_view(), name='create-label'),
    path('labelupdate/<int:id>/', views.LabelUpdateView.as_view(), name='label-update'),
]