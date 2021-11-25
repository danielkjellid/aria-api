from rest_framework import serializers


class LogEntrySerializer(serializers.Serializer):
    """
    A serializer to display audit logs associated with a specific instance
    """

    user = serializers.CharField()
    change = serializers.JSONField()
    date_of_change = serializers.DateTimeField()
