from django.shortcuts import render, get_object_or_404
from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer, LabelSerializer
from .models import Notes, Label
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from rest_framework import generics

import json
import redis
from django.conf import settings
# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

from rest_framework.filters import SearchFilter, OrderingFilter

import logging
from Fundoo.settings import file_handler

from rest_framework import status

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
        # print(user)
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
            redis_note_create = serializer.save(user_id=user.id)
            logger.info("New Note is created.")
            redis_instance.hmset(str(user.id)+"note", {redis_note_create.id: str(json.dumps(serializer.data))})
            # print(redis_instance.hgetall(str(user.id)+ "note"))
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
            # print(user)
            queryset = Notes.objects.filter(user_id=user.id)
            # print(queryset)
            return get_object_or_404(queryset, id=id)
        except Notes.DOesNotExit:
            logger.error("id not present, from get_object()")
            return Response({'details': 'Id not present'})

    def get(self, request, id):
        try:
            user = request.user
            note = self.get_object(request, id)
            serializer = NotesSerializer(note)
            logger.info("got Note successfully, from get()")
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
                redis_instance.hmset(str(user.id)+"note", {note_update.id: str(json.dumps(serializer.data))})
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
            redis_instance.hdel(str(user.id)+"note", id)
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
            redis_instance.hmset(str(user.id)+"label",{create_label.id:label})
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
                update_label = serializer.save()
                logger.info("Label Updated successfully, from put()")
                return Response({'details': 'Label Updated successfully'}, status=200)
            logger.error("Label not Updated, from put()")
            redis_instance.hmset(str(user.id)+"label",{update_label.id:label})
            return Response({'details': 'Label not Updated'}, status=400)
        except:
            logger.error("Label is not present, from put()")
            return Response({'details': 'Label is is not present'}, status=404)


    def delete(self, request, id):
        try:
            data = request.data
            instance = self.get_object(request, id)
            instance.delete()
            redis_instance.hdel(str(user.id)+"label",id)
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
            archive_redis_data = redis_instance.hvals(str(user.id)+"is_archive")
            if len(archive_redis_data) > 0:
                serializer = NotesSerializer(archive_redis_data, many=True)
                print("Data from redis")
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
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, is_archive=True)


class SearchBoxView(generics.ListAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'note', 'user__username']


