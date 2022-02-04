from django.conf import settings
from rest_framework import serializers

from aria.core.serializers import BaseHeaderImageSerializer, BaseListImageSerializer
from aria.product_categorization.models import Category, SubCategory


class SubCategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = SubCategory
        fields = ("id", "name", "slug", "ordering")
        read_only_fields = fields


class CategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer used in the navigational bar of the application
    """

    slug = serializers.SlugField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "children")
        read_only_fields = fields

    def get_children(self, instance):
        children = instance.children.filter(sites=settings.SITE_ID).order_by("ordering")
        return SubCategoryNavigationListSerializer(
            children, many=True, read_only=True
        ).data


class CategoryListSerializer(serializers.ModelSerializer):
    """
    A serializer to display the top level categories and associated images in app
    """

    images = BaseHeaderImageSerializer(source="*", read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "ordering",
            "width",
            "images",
        )
        read_only_fields = fields


class CategorySerializer(serializers.Serializer):
    """
    A serializer to display a specific category instance
    """

    name = serializers.CharField()
    images = BaseHeaderImageSerializer(source="*", read_only=True)


class SubCategoryListSerializer(serializers.ModelSerializer):

    images = BaseListImageSerializer(source="*", read_only=True)

    class Meta:
        model = SubCategory
        fields = ("id", "name", "slug", "description", "ordering", "images")
        read_only_fields = fields
