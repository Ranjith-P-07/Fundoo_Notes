from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer
from .models import Notes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from rest_framework import generics






@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteCreateView(GenericAPIView):
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    def get(self, request):
        user = request.user
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

