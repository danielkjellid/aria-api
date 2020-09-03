from rest_framework import serializers
from inventory.models import Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'slug')
        

class CategoryNavigationSerializer(serializers.ModelSerializer):
    """
    A serializer used in the navigational bar of the application
    """

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children')

    def get_children(self, instance):
        children = instance.children.all().order_by('ordering')
        return SubCategorySerializer(children, many=True, read_only=True).data


class CategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display the top level categories and associated images in app
    """

    image_512x512 = serializers.ImageField(read_only=True)
    image_1024x1024 = serializers.ImageField(read_only=True)
    image_1536x1536 = serializers.ImageField(read_only=True)
    image_1024x576 = serializers.ImageField(read_only=True)
    image_1536x864 = serializers.ImageField(read_only=True)
    image_2048x1152 = serializers.ImageField(read_only=True)
    image_2560x1440 = serializers.ImageField(read_only=True)
    image_3072x1728 = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
            'ordering',
            'width',
            'image',
            'image_512x512',
            'image_1024x1024',
            'image_1536x1536',
            'image_1024x576',
            'image_1536x864',
            'image_2048x1152',
            'image_2560x1440',
            'image_3072x1728',
        )