from rest_framework import serializers
from inventory.models import Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'slug')
        

class CategorySerializer(serializers.ModelSerializer):
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

    
