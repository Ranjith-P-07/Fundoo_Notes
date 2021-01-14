from django.shortcuts import render, get_object_or_404
from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer, LabelSerializer
from .models import Notes, Label
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

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

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)




@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ListNoteView(generics.ListAPIView):
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
        if serializer.is_valid():
            note = serializer.save(user_id=user.id)
            logger.info("New Note is created.")
            cache.set(str(user.id)+"note"+str(note.id), note)
            if cache.get(str(user.id)+"note"+str(note.id)):
                logger.info("Data is stored in cache")
            return Response(serializer.data, status=201)
        logger.error("Something went wrong whlie creating Note, from post()")
        return Response(serializer.data, status=400)


@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteUpdateView(GenericAPIView):
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
        except:
            logger.error("Something went wrong")
            return Response(status=404)
        # except Exception as e:
        #     logger.error("Something went wrong")
        #     return Response(e)


    def delete(self, request, id):
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            instance.delete()
            cache.delete(str(user.id)+"note"+str(id))
            logger.info("Note is Deleted Succesfully, from delete()")
            return Response({'details': 'Note is Deleted'}, status=204)
        except:
            logger.error("Something went wrong")
            return Response({'details': 'Note is not deleted..'}, status=404)



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
                return Response(serializer.data, status=200)
            else:
                archive_db_data = Notes.objects.filter(user_id = user.id, is_archive=True)
                if len(archive_db_data) > 0:
                    serializer = NotesSerializer(archive_db_data, many=True)
                    print("Data from Database")
                    # redis_instance.hmset(str(user.id)+"is_archive", {archive_db_data.id: str(json.dumps(serializer.data))})
                    # print(redis_instance.hgetall(str(user.id)+"is_archive"))
                    return Response(serializer.data, status=200)
                else:
                    return Response("Archive data not available", status=400)
        except Exception as e:
            return Response(e)
        # except:
        #     return Response("something went wrong", status=400)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class TrashNoteAPI(generics.ListAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, is_archive=True)


class SearchBoxView(generics.ListAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'note', 'user__username']


class CollaboratorAPIView(GenericAPIView):
    queryset = Notes.objects.all()
    def get(self, request):
        user = request.user
        temp = []
        try:
            collabrator = Notes.objects.filter(user_id = user.id, collabrator__isnull=False,is_trashed =False)
            print(collabrator)
            if len(collabrator)>0:
                collabrator_list = collabrator.values('collabrator','title')
                print(collabrator_list)
                
                for i in range(len(collabrator_list)):
                    print(i)
                    print(collabrator_list[i]['collabrator'])
                    collabrator_id = collabrator_list[i]['collabrator']
                    print(collabrator_id)
                    collabrator1 = User.objects.filter(id = collabrator_id)
                    collabrator_email = collabrator1.values('email')
                    print(collabrator_email[0])
                    print(collabrator_list[i])
                    collabrator_list[i].update(collabrator_email[0])
                    temp = temp + [collabrator_list[i]]
                    print(temp)
                return Response(temp, status=200)
            else:
                return Response("No such Note available to have any collabrator Added")
        except Exception as e:
            return Response(e)