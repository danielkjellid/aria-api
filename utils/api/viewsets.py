from rest_framework import filters, generics, permissions, status

from utils.models import Note
from utils.api.serializers import NoteListSerializer

class NoteDeleteAPIView(generics.DestroyAPIView):
    queryset = Note.objects.all()