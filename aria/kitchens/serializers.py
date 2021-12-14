from rest_framework import serializers

from aria.core.serializers import BaseHeaderImageSerializer
from aria.kitchens.models import Kitchen


class InstanceColorSerializer(serializers.Serializer):
    """
    A serializer to display name and color hex
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    color_hex = serializers.CharField(read_only=True)


class KitchenVariantImageSerializer(serializers.Serializer):
    """
    Serializer for kitchen variants which uses an image instead of a color
    """

    name = serializers.CharField(read_only=True)
    image = serializers.CharField(source="thumbnail.url")


class KitchenListSerializer(serializers.ModelSerializer):
    """
    Serializer for getting a list over kitchens
    """

    thumbnail_500x305 = serializers.ImageField(read_only=True)
    thumbnail_660x400 = serializers.ImageField(read_only=True)
    thumbnail_850x520 = serializers.ImageField(read_only=True)

    class Meta:
        model = Kitchen
        fields = (
            "id",
            "name",
            "slug",
            "thumbnail_description",
            "thumbnail_500x305",
            "thumbnail_660x400",
            "thumbnail_850x520",
        )
        read_only_fields = fields


class KitchenSerializer(serializers.ModelSerializer):
    """
    Serializer for getting a specific kitchen instance
    """

    example_from_price = serializers.DecimalField(decimal_places=2, max_digits=8)
    silk_variants = InstanceColorSerializer(read_only=True, many=True)
    decor_variants = KitchenVariantImageSerializer(read_only=True, many=True)
    plywood_variants = KitchenVariantImageSerializer(read_only=True, many=True)
    laminate_variants = InstanceColorSerializer(read_only=True, many=True)
    exclusive_variants = InstanceColorSerializer(read_only=True, many=True)
    trend_variants = InstanceColorSerializer(read_only=True, many=True)
    images = BaseHeaderImageSerializer(source="*", read_only=True)

    class Meta:
        model = Kitchen
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "apply_filter",
            "extra_description",
            "example_from_price",
            "can_be_painted",
            "silk_variants",
            "decor_variants",
            "plywood_variants",
            "laminate_variants",
            "exclusive_variants",
            "trend_variants",
            "images",
        )
        read_only_fields = fields
