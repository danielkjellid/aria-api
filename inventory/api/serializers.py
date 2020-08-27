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
    
    children = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'children')

    
