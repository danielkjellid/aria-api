from rest_framework import serializers
from utils.models import Note


class NoteListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = '__all__'


class CreateNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ('note', )


class UpdateNoteSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    note = serializers.CharField()