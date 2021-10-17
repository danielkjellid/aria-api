from rest_framework import serializers
from notes.models import NoteEntry


class NoteListSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoteEntry
        fields = '__all__'


class CreateNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoteEntry
        fields = ('note', )


class UpdateNoteSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    note = serializers.CharField()