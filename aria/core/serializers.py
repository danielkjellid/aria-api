from django.db.models.query import QuerySet
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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


class BaseListImageSerializer(serializers.Serializer):
    """
    A serializer that serializes list images. Values
    are inherited by BaseListImageModel in core.models.
    """

    image500x305 = serializers.CharField(source="image500x305.url", read_only=True)
    image600x440 = serializers.CharField(source="image600x440.url", read_only=True)
    image850x520 = serializers.CharField(source="image850x520.url", read_only=True)

    class Meta:
        fields = "image500x305" "image600x440" "image850x520"
        abstract = True


def _create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    """
    The inline serializer is to be used for nested serialization within
    the viewset.
    """

    serializer_class = _create_serializer_class(name="", fields=fields)

    if data is not None:
        if isinstance(data, QuerySet):
            return serializer_class(data=[d for d in data], **kwargs)

        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)
