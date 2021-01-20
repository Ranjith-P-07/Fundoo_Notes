from django.urls import path
from .views import NoteCreateView, LabelCreateView, LabelUpdateView, TrashNoteAPI, ArchiveNoteView, CollaboratorAPIView, UnTrashNoteAPI, UnArchieveNoteAPI
from . import views

urlpatterns = [
    path('archive-note/', views.ArchiveNoteView.as_view(), name='Archive_note'),
    path('collabrator/', views.CollaboratorAPIView.as_view(), name='collaborator_note'),
    path('list/', views.ListNoteView.as_view(), name='note-list'),
    path('label/', views.LabelCreateView.as_view(), name='create_label'),
    path('labelupdate/<int:id>/', views.LabelUpdateView.as_view(), name='label_update'),
    path('note/', views.NoteCreateView.as_view(), name='create_note'),
    path('noteupdate/<int:id>/', views.NoteUpdateView.as_view(), name='note_update'),
    path('reminder-note/<int:id>/', views.ReminderAPIView.as_view(), name='note_reminder'),
    path('search-note/', views.SearchBoxView.as_view(), name='Search_note'),
    path('trash-note/', views.TrashNoteAPI.as_view(), name='Trash_note'),
    path('unarchive-note/<int:id>/', views.UnArchieveNoteAPI.as_view(), name='UnArchive_note'),
    path('untrash-note/<int:id>/', views.UnTrashNoteAPI.as_view(), name='UnTrash_note'),
]