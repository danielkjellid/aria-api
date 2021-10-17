from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from core.permissions import HasUserOrGroupPermission

from utils.models import Note

class NoteDeleteAPIView(generics.DestroyAPIView):
    queryset = Note.objects.all()
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {
        'DELETE': ['has_note_delete']
    }
    