from django.urls import path
from .views import NoteCreateView, LabelCreateView, LabelUpdateView, TrashNoteAPI, ArchiveNoteView
from . import views

urlpatterns = [
    path('note/', views.NoteCreateView.as_view(), name='create_note'),
    path('list/', views.ListNoteView.as_view(), name='note-list'),
    path('noteupdate/<int:id>/', views.NoteUpdateView.as_view(), name='note-update'),
    path('label/', views.LabelCreateView.as_view(), name='create_label'),
    path('labelupdate/<int:id>/', views.LabelUpdateView.as_view(), name='label_update'),
    path('trash-note/', views.TrashNoteAPI.as_view(), name='Trash_note'),
    path('Archive-note/', views.ArchiveNoteView.as_view(), name='Archive_note'),
    path('Search-note/', views.SearchBoxView.as_view(), name='Search_note'),
]