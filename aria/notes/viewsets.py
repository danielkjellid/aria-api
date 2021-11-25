from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from aria.core.permissions import HasUserOrGroupPermission

from aria.notes.models import NoteEntry


class NoteDeleteAPIView(generics.DestroyAPIView):
    queryset = NoteEntry.objects.all()
    permission_classes = (IsAdminUser, HasUserOrGroupPermission)
    required_permissions = {"DELETE": ["has_note_delete"]}
