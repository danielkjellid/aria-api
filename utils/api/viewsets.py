from rest_framework import filters, generics, permissions, status
from rest_framework.permissions import IsAdminUser

from core.permissions import HasUserOrGroupPermission

from utils.models import Note
from utils.api.serializers import NoteListSerializer

class NoteDeleteAPIView(generics.DestroyAPIView):
    queryset = Note.objects.all()
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'DELETE': ['has_note_delete']
    }
    