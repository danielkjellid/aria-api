from rest_framework import serializers
from utils.models import Note

class AuditLogSerializer(serializers.Serializer):
    """
    A serializer to display audit logs associated with a specific instance
    """

    user = serializers.CharField()
    change = serializers.JSONField()
    date_of_change = serializers.DateTimeField()


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