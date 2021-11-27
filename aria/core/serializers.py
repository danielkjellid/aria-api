from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = "username"

    default_error_messages = {
        "no_active_account": "Feil brukernavn eller passord. Merk at du må skille mellom store og små bokstaver."
    }


class BaseHeaderImageSerializer(serializers.Serializer):
    """
    A serializer that serializes header images. Values
    are inherited by BaseHeaderImageModel in core.models.
    """

    apply_filter = serializers.BooleanField()
    image_512x512 = serializers.CharField(source="image_512x512.url", read_only=True)
    image_640x275 = serializers.CharField(source="image_640x275.url", read_only=True)
    image_1024x1024 = serializers.CharField(
        source="image_1024x1024.url", read_only=True
    )
    image_1024x575 = serializers.CharField(source="image_1024x575.url", read_only=True)
    image_1536x860 = serializers.CharField(source="image_1536x860.url", read_only=True)
    image_2048x1150 = serializers.CharField(
        source="image_2048x1150.url", read_only=True
    )

    class Meta:
        fields = (
            "apply_filter",
            "image_512x512",
            "image_640x275",
            "image_1024x1024",
            "image_1024x575",
            "image_1536x860",
            "image_2048x1150",
        )
        abstract = True
