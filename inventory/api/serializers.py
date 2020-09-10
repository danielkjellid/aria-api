from rest_framework import serializers
from inventory.models import Category, SubCategory, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display name of (sub)categories
    """

    class Meta:
        model = Category
        fields = ['name']


class SubCategoryNavigationListSerializer(serializers.ModelSerializer):
    """
    A serializer to display category children for a given category
    """

    slug = serializers.SlugField(read_only=True)

    class Meta: 
        model = SubCategory
        fields = ('id', 'name', 'slug')
        

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
        return SubCategoryNavigationSerializer(children, many=True, read_only=True).data


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


class ProductListByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display products by (sub)category
    """

    price = serializers.SerializerMethodField()
    subcategory = CategorySerializer(many=True, source='category')
    colors = serializers.StringRelatedField(read_only=True, many=True)
    rooms = serializers.StringRelatedField(read_only=True, many=True)
    styles = serializers.StringRelatedField(read_only=True, many=True)
    application = serializers.StringRelatedField(read_only=True, many=True)
    material = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'unit',
            'price',
            'can_be_purchased_online',
            'subcategory',
            'colors',
            'rooms',
            'styles',
            'application',
            'material',
        )

    def get_price(self, product):
        """
        Method to calculate gross price
        """
        
        vat = product.net_price * product.vat_rate
        gross_price = product.net_price + vat

        return gross_price