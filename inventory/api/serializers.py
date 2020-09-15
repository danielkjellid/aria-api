from rest_framework import serializers
from inventory.models import Category, SubCategory, Product


class SubCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display name of (sub)categories
    """

    class Meta:
        model = SubCategory
        fields = ['name']


class SubCategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    slug = serializers.SlugField(read_only=True)

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'slug', 'ordering')


class SubCategoryFilterListSerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'ordering')
        

class CategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer used in the navigational bar of the application
    """

    slug = serializers.SlugField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children')

    def get_children(self, instance):
        children = instance.children.all().order_by('ordering')
        return SubCategoryNavigationListSerializer(children, many=True, read_only=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    """
    A serializer to display the top level categories and associated images in app
    """

    slug = serializers.SlugField(read_only=True)
    image_512x512 = serializers.ImageField(read_only=True)
    image_1024x1024 = serializers.ImageField(read_only=True)
    image_1536x1536 = serializers.ImageField(read_only=True)
    image_1024x480 = serializers.ImageField(read_only=True)
    image_1536x660 = serializers.ImageField(read_only=True)
    image_2048x800 = serializers.ImageField(read_only=True)
    image_2560x940 = serializers.ImageField(read_only=True)
    image_3072x940 = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
            'ordering',
            'width',
            'image_512x512',
            'image_1024x1024',
            'image_1536x1536',
            'image_1024x480',
            'image_1536x660',
            'image_2048x800',
            'image_2560x940',
            'image_3072x940',
        )
        read_only_fields = fields


class ProductListByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display products by (sub)category
    """

    price = serializers.SerializerMethodField()
    categories = SubCategorySerializer(source='category', read_only=True, many=True)
    colors = serializers.StringRelatedField(read_only=True, many=True)
    styles = serializers.StringRelatedField(read_only=True, many=True)
    applications = serializers.StringRelatedField(read_only=True, many=True)
    materials = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'unit',
            'price',
            'can_be_purchased_online',
            'categories',
            'colors',
            'styles',
            'applications',
            'materials',
        )

    def get_price(self, product):
        """
        Method to calculate gross price
        """
        
        vat = product.net_price * product.vat_rate
        gross_price = product.net_price + vat

        return gross_price


class ProductFiltersByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display available filters for a product lust 
    """

    class Meta:
        model = Product
        fields = '__all__'