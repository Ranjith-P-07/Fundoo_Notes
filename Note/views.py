from django.shortcuts import render, get_object_or_404
from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer, LabelSerializer, ReminderSerializer
from .models import Notes, Label
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from rest_framework import generics

import json
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.conf import settings
import redis_cache

from django.contrib.auth.models import User


from rest_framework.filters import SearchFilter, OrderingFilter

import logging
from Fundoo.settings import file_handler

from rest_framework import status
from django.db.models import Q

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)




@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ListNoteView(generics.ListAPIView):
    """
    Summary:
    --------
        All the notes will be listed for the user.
    """
    serializer_class = NotesSerializer  
    queryset = Notes.objects.all()
    logger.info("Notes listed succesfully..!!")




@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteCreateView(GenericAPIView):
    """
        Summary:
        --------
            Note class will let authorized user to create and get notes.
        --------
        Methods:
            get: User will get all the notes.
            post: User will able to create new note.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    lookup_field = 'id'

    def get(self, request):
        """
            Summary:
            --------
                All the notes will be fetched for the user.
            --------
            Exception:
                PageNotAnInteger: object
                EmptyPage: object.
        """
        user = request.user
        notes = Notes.objects.filter(user_id = user.id, is_archive=False)
        serializer = NotesSerializer(notes, many=True)
        logger.info("Particular Note is obtained, from get()")
        return Response(serializer.data, status=200)


    def post(self, request):
        """
            Summary:
            --------
                New note will be create by the User.
            Exception:
            ----------
                KeyError: object
        """
        data = request.data
        user = request.user
        serializer = NotesSerializer(data=data, partial=True)
        print(serializer)
        if serializer.is_valid():
            note = serializer.save(user_id=user.id)
            logger.info("New Note is created.")
            cache.set(str(user.id)+"note"+str(note.id), note)
            logger.info("Data is stored in cache")
            return Response(serializer.data, status=201)
        logger.error("Something went wrong whlie creating Note, from post()")
        return Response(serializer.data, status=400)


@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteUpdateView(GenericAPIView):
    """
        Summary:
        --------
            Existing note can be updated / deleted  by the User.
        Exception:
        ----------
            KeyError: object
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_object(self, request, id):
        try:
            user = request.user
            queryset = Notes.objects.filter(user_id=user.id)
            return get_object_or_404(queryset, id=id)
        except Notes.DoesNotExist:
            logger.error("id not present, from get_object()")
            return Response({'details': 'Id not present'})

    def get(self, request, id):
        try:
            user = request.user
            if cache.get(str(user.id)+"note"+str(id)):
                note = cache.get(str(user.id)+"note"+str(id))
                serializer = NotesSerializer(note)
                print("data from cache")
                return Response(serializer.data)
            else:
                note = self.get_object(request, id)
                serializer = NotesSerializer(note)
                logger.info("got Note successfully, from get()")
                print("data from db")
                return Response(serializer.data, status=200)
        except:
            logger.error("something went wrong while getting Note, Enter the right id, from get()")
            return Response(status=404)

    def put(self, request, id):
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            serializer = NotesSerializer(instance, data=data)
            if serializer.is_valid():
                note_update = serializer.save(user_id=user.id)
                logger.info("Note updated succesfully, from put()")
                cache.set(str(user.id)+"note"+str(id), note_update)
                return Response({'details': 'Note updated succesfully'}, status=200)
            logger.error("Note is not Updated something went wrong, from put()")
            return Response({'deatils': 'Note is not Updated..!!!'}, status=400)
        # except:
        #     logger.error("Something went wrong")
        #     return Response(status=404)
        except Exception as e:
            logger.error("Something went wrong")
            return Response(e)


    def delete(self, request, id):
        user = request.user
        try:
            # data = request.data
            instance = self.get_object(request, id)
            # print(instance)
            if instance.is_trashed:
                instance.delete()
                logger.info("Note is Deleted Permanently, from delete()")
                return Response({'details': 'Note is Deleted'}, status=200)
            else:
                instance.is_trashed = True
                instance.trashed_time = datetime.now()
                instance.save()
                logger.info("Note is Trashed")
                return Response({'details': 'Your note is Trashed'}, status=200)
        # except Exception as e:
        #     return Response(e)
        except:
            logger.error("Note does not exist ")
            return Response({'details': 'Note is not exist'}, status=404)



@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class LabelCreateView(GenericAPIView):
    """
        Summary:
        --------
            LabelCreate class will let authorized user to create and get labels.
        --------
        Methods:
            get: User will get all the labels.
            post: User will able to create new label.
    """
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):
        """
            Summary:
            --------
                All the labels will be fetched for the user.
            --------
            Exception:
                PageNotAnInteger: object
                EmptyPage: object.
        """
        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(labels, many=True)
            logger.info("Got the Labels, from get()")
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error("Something went wrong, from get()")
            return Response(e)

    def post(self, request):
        """
            Summary:
            --------
                New note will be create by the User.
            Exception:
            ----------
                KeyError: object
        """
        user = request.user
        try:
            label=request.data['labelname']
            if label == "":
                logger.error("labelname should be blank, from post()")
                return Response({'details': 'labelname should be blank'}, status=204)
            if Label.objects.filter(user_id=user.id, labelname=label).exists():
                logger.error("label already exists, from post()")
                return Response({'details': 'label already exists'})
            create_label = Label.objects.create(labelname=label, user_id=user.id)
            logger.info("New Label is created.")
            cache.set(str(user.id)+"label"+str(create_label.id), create_label)
            return Response({'details': 'new label created'}, status=201)
        except Exception as e:
            logger.error("Something went wrong")
            return Response(e)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class LabelUpdateView(GenericAPIView):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get_object(self, request, id):
        try:
            user = request.user
            queryset = Label.objects.filter(user_id=user.id)
            return get_object_or_404(queryset, id=id)
        except:
            logger.error("id not present, from get_object()")
            return Response({'details': 'id not present'})

    def get(self, request, id):
        if cache.get(str(user.id)+"label"+str(update_label.id)):
            instance = cache.get(str(user.id)+"label"+str(update_label.id))
            serializer = LabelSerializer(instance)
            return Response(serializer.data)
        else:
            instance = self.get_object(request, id)
            serializer = LabelSerializer(instance)
            logger.info("Got Label object, from get()")
            return Response(serializer.data, status=200)

    def put(self, request, id):
        user = request.user
        try:
            data = request.data
            label = request.data['labelname']
            instance = self.get_object(request, id)
            serializer = LabelSerializer(instance, data=data)
            if serializer.is_valid():
                update_label = serializer.save(user_id=user.id)
                logger.info("Label Updated successfully, from put()")
                return Response({'details': 'Label Updated successfully'}, status=200)
            logger.error("Label not Updated, from put()")
            cache.set(str(user.id)+"label"+str(update_label.id), update_label)
            return Response({'details': 'Label not Updated'}, status=400)
        except:
            logger.error("Label is not present, from put()")
            return Response({'details': 'Label is is not present'}, status=404)


    def delete(self, request, id):
        try:
            data = request.data
            instance = self.get_object(request, id)
            instance.delete()
            cache.delete(str(user.id)+"label"+str(update_label.id))
            logger.info("Label deleted succesfully, from delete()")
            return Response({'details': 'Label deleted succesfully'}, status=204)
        except:
            logger.error("Label not deleted, from delete()")
            return Response({'details': 'Label not deleted'}, status=404)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ArchiveNoteView(GenericAPIView):
    """
    Summary:
    --------
        All the ArchiveNotes  will be listed for the user.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    lookup_field = 'id'

    def get(self, request):
        user = request.user
        try:
            archive_redis_data = redis_instance.hvals(str(user.id)+"note")
            if len(archive_redis_data) > 0:
                serializer = NotesSerializer(archive_redis_data, many=True)
                print("Data from redis")
                logger.info("ArchivedNotes are listed")
                return Response(serializer.data, status=200)
            else:
                archive_db_data = Notes.objects.filter(user_id = user.id, is_archive=True)
                if len(archive_db_data) > 0:
                    serializer = NotesSerializer(archive_db_data, many=True)
                    print("Data from Database")
                    return Response(serializer.data, status=200)
                else:
                    return Response("Archive data not available", status=400)
        except Exception as e:
            return Response(e)
        # except:
        #     return Response("something went wrong", status=400)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class TrashNoteAPI(generics.ListAPIView):
    """
    Summary:
    --------
        All the Trashed notes will be listed for the user.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_queryset(self):
        logger.info("Trashed Notes are Listed")
        return self.queryset.filter(user=self.request.user, is_trashed=True)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class UnTrashNoteAPI(GenericAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_object(self, request, id):
        try:
            user = request.user
            queryset = Notes.objects.filter(user_id=user.id, is_trashed=True)
            return get_object_or_404(queryset, id=id)
        except Notes.DoesNotExist:
            logger.error("id not present, from get_object()")
            return Response({"response": "id not present"}, status=404)

    def get(self, request, id):
        try:
            user = request.user
            mynote = self.get_object(request, id)
            serializer = NotesSerializer(mynote)
            logger.info("Retrieved specific id, from get()")
            return Response({"response": serializer.data}, status=200)
        except Exception:
            logger.error("can't get this id, from get()")
            return Response({"response": "can't get this id / it is not trashed"}, status=404)

    def put(self, request, id):
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            serializer = NotesSerializer(instance, data=data)

            if serializer.is_valid():
                note_update = serializer.save(user_id=user.id)
                is_trashed_check = serializer.data["is_trashed"]
                if is_trashed_check == False:
                    logger.info("Note untrashed successfully")
                    return Response({"response": "Note untrashed successfully"}, status=200)
                else:
                    logger.error("Note untrash failed, Note present in trash only")
                    return Response({"response": "Note UnTrashed failed,Note present in Trash only"}, status=400)
        except:
            logger.error("Failed to UnTrash Note, from put()")
            return Response({"response": "Failed to unTrash"}, status=400)



@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class SearchBoxView(GenericAPIView):
    """
        Summary:
        --------
            All the Searched data by user is listed based on title and note.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_search(self, search_query=None):
        user = self.request.user
        if search_query:
            search_split = search_query.split(' ')
            print(search_split)
            for query in search_split:
                if cache.get(search_split):
                    result = cache.get(search_split)
                    logger.info("data from cache")
                else:
                    note = Notes.objects.filter(user_id=user.id, is_trashed=False)
                    result = note.filter(Q(title__icontains=query)|Q(note__icontains=query))
                    if result:
                        cache.set(search_split, result)
                        logger.info("Data from db")
        else:
            result = Notes.objects.filter(user_id=user.id)
            logger.info("All Notes listed")
        return result

    def get(self, request):
        search_query = request.GET.get('search')
        if search_query:
            result = self.get_search(search_query)
            logger.info("Obtained collaborated Notes")
        else:
            result = self.get_search()
        serializer = NotesSerializer(result, many=True)
        logger.info("all notes are listed")
        return Response(serializer.data, status=200)


@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class CollaboratorAPIView(GenericAPIView):
    """
        Summary:
        --------
            Collaborator is added to particular note.
        Exception:
        ----------
            KeyError: object
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    def get(self, request):
        user = request.user
        num_collaborator = []
        try:
            collabrator = Notes.objects.filter(user_id = user.id, collabrator__isnull=False,is_trashed =False)
            if (collabrator):
                collabrator_list = collabrator.values('collabrator','title')
                
                for i in range(len(collabrator_list)):
                    collabrator_id = collabrator_list[i]['collabrator']
                    collabrator1 = User.objects.filter(id = collabrator_id)
                    collabrator_email = collabrator1.values('email')
                    collabrator_list[i].update(collabrator_email[0])
                    num_collaborator = num_collaborator + [collabrator_list[i]]
                return Response(num_collaborator, status=200)
            else:
                logger.info("No such Note available to have any collabrator Added")
                return Response({"Details" : "No such Note available to have any collabrator Added"}, status=404)
        except Exception as e:
            return Response(e)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ReminderAPIView(GenericAPIView):
    """
        Summary:
        --------
            This API will remindes user at the date and time specified by the user.
        Exception:
        ----------
            Not Found error
    """
    serializer_class = ReminderSerializer
    # queryset = Notes.objects.all()

    def patch(self, request, id):
        try:
            user = request.user
            note = Notes.objects.get(user_id=user.id, id=id)
            serializer = ReminderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            note.reminder = serializer.data.get('reminder')
            note.save()
            logger.info("Reminder is set")
            return Response({'details': 'Reminder is set'}, status=200)
        except:
            logger.error("Note not found, from ()patch")
            return Response({"Details" : "Note not found"}, status=404)

