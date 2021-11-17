import os
from core.models import BaseHeaderImageModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.conf import settings


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = 'username'

    default_error_messages = {
        'no_active_account': 'Feil brukernavn eller passord. Merk at du må skille mellom store og små bokstaver.'
    }


class BaseHeaderImageSerializer(serializers.Serializer):

    apply_filter = serializers.BooleanField()
    image_512x512 = serializers.SerializerMethodField()
    image_640x275 = serializers.SerializerMethodField()
    image_1024x1024 = serializers.SerializerMethodField()
    image_1024x575 = serializers.SerializerMethodField()
    image_1536x860 = serializers.SerializerMethodField()
    image_2048x1150 = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'apply_filter',
            'image_512x512',
            'image_640x275',
            'image_1024x1024',
            'image_1024x575',
            'image_1536x860',
            'image_2048x1150'
        )
        abstract = True

    def _get_image(self, image):
        return os.path.join(settings.MEDIA_URL, str(image))

    def get_image_512x512(self, image):
        return self._get_image(image.image_512x512)

    def get_image_640x275(self, image):
        return self._get_image(image.image_640x275)

    def get_image_1024x1024(self, image):
        return self._get_image(image.image_1024x1024)

    def get_image_1024x575(self, image):
        return self._get_image(image.image_1024x575)

    def get_image_1536x860(self, image):
        return self._get_image(image.image_1536x860)

    def get_image_2048x1150(self, image):
        return self._get_image(image.image_2048x1150)
