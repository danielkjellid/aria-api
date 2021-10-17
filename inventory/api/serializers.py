import os
from django.conf import settings

from inventory.models.category import Category, SubCategory
from rest_framework import serializers

# generic serializers
class InstanceColorSerializer(serializers.Serializer):
    """
    A serializer to display name and color hex
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    color_hex = serializers.CharField(read_only=True)


# category serializers
class SubCategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    slug = serializers.SlugField(read_only=True)

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'slug', 'ordering')
        read_only_fields = fields
        

class CategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer used in the navigational bar of the application
    """

    slug = serializers.SlugField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children')
        read_only_fields = fields

    def get_children(self, instance):
        children = instance.children.filter(sites=settings.SITE_ID).order_by('ordering')
        return SubCategoryNavigationListSerializer(children, many=True, read_only=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    """
    A serializer to display the top level categories and associated images in app
    """
    image_512x512 = serializers.SerializerMethodField()
    image_1024x1024 = serializers.SerializerMethodField()
    image_1024x480 = serializers.SerializerMethodField()
    image_1536x660 = serializers.SerializerMethodField()
    image_2048x800 = serializers.SerializerMethodField()
    image_2560x940 = serializers.SerializerMethodField()
    image_3072x940 = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
            'ordering',
            'width',
            'apply_filter',
            'image_512x512',
            'image_1024x1024',
            'image_1024x480',
            'image_1536x660',
            'image_2048x800',
            'image_2560x940',
            'image_3072x940',
        )
        read_only_fields = fields

    def get_image_512x512(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_512x512))

    def get_image_1024x1024(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1024x1024))

    def get_image_1024x480(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1024x480))

    def get_image_1536x660(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1536x660))

    def get_image_2048x800(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_2048x800))

    def get_image_2560x940(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_2560x940))

    def get_image_3072x940(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_3072x940))


class CategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display a specific category instance
    """

    image_512x512 = serializers.SerializerMethodField()
    image_1024x1024 = serializers.SerializerMethodField()
    image_1024x480 = serializers.SerializerMethodField()
    image_1536x660 = serializers.SerializerMethodField()
    image_2048x800 = serializers.SerializerMethodField()
    image_2560x940 = serializers.SerializerMethodField()
    image_3072x940 = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'name',
            'apply_filter',
            'image_512x512',
            'image_1024x1024',
            'image_1024x480',
            'image_1536x660',
            'image_2048x800',
            'image_2560x940',
            'image_3072x940',
        )
        read_only_fields = fields

    def get_image_512x512(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_512x512))

    def get_image_1024x1024(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1024x1024))

    def get_image_1024x480(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1024x480))

    def get_image_1536x660(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_1536x660))

    def get_image_2048x800(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_2048x800))

    def get_image_2560x940(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_2560x940))

    def get_image_3072x940(self, category):
        return os.path.join(settings.MEDIA_URL, str(category.image_3072x940))
