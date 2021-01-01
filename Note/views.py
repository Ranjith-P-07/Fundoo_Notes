from django.shortcuts import render, get_object_or_404
from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer, LabelSerializer
from .models import Notes, Label
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from rest_framework import generics



@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ListNoteView(generics.ListAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()



@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteCreateView(GenericAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    def get(self, request):
        user = request.user
        print(user)
        notes = Notes.objects.filter(user_id = user.id, is_archive=False)
        serializer = NotesSerializer(notes, many=True)
        return Response(serializer.data, status=200)


    def post(self, request):
        data = request.data
        user = request.user
        serializer = NotesSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save(user_id=user.id)
            return Response(serializer.data, status=201)
        return Response(serializer.data, status=400)


@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteUpdateView(GenericAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_object(self, request, id):
        try:
            user = request.user
            print(user)
            queryset = Notes.objects.filter(user_id=user.id)
            print(queryset)
            return get_object_or_404(queryset, id=id)
        except Notes.DOesNotExit:
            return Response({'details': 'Id not present'})

    def get(self, request, id):
        try:
            user = request.user
            note = self.get_object(request, id)
            serializer = NotesSerializer(note)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response(e)

    def put(self, request, id):
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            serializer = NotesSerializer(instance, data=data)
            if serializer.is_valid():
                note_update = serializer.save(user_id=user.id)
                return Response({'details': 'Note updated succesfully'})
            return Response({'deatils': 'Note is not Updated..!!!'})
        except Exception as e:
            return Response(e)

    def delete(self, request, id):
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            instance.delete()
            return Response({'details': 'Note is Deleted'})
        except:
            return Response({'details': 'Note is not deleted..'})




class LabelCreateView(GenericAPIView):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):
        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(labels, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response(e)

    def post(self, request):
        user = request.user
        try:
            label=request.data['labelname']
            if label == "":
                return Response({'details': 'labelname should be blank'})
            if Label.objects.filter(user_id=user.id, labelname=label).exists():
                return Response({'details': 'label already exists'})
            create_label = Label.objects.create(labelname=label, user_id=user.id)
            return Response({'details': 'new label created'})
        except Exception as e:
            return Response(e)