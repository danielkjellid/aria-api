from django.urls import path

from utils.api.viewsets import NoteDeleteAPIView


urlpatterns = [
    # endpoint for getting info about request user
    path('utils/notes/<int:pk>/delete/', NoteDeleteAPIView.as_view(), name='notes'),
]