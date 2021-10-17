from django.urls import path

from notes.viewsets import NoteDeleteAPIView


urlpatterns = [
    # endpoint for getting info about request user
    path('utils/notes/<int:pk>/delete/', NoteDeleteAPIView.as_view(), name='notes'),
]