from rest_framework import serializers
from inventory.models import Category, SubCategory, Product, ProductColor, ProductVariant


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
        children = instance.children.all().order_by('ordering')
        return SubCategoryNavigationListSerializer(children, many=True, read_only=True).data


class CategoryListSerializer(serializers.Serializer):
    """
    A serializer to display the top level categories and associated images in app
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    ordering = serializers.IntegerField(read_only=True)
    width = serializers.CharField(read_only=True)
    image_512x512 = serializers.ImageField(read_only=True)
    image_1024x1024 = serializers.ImageField(read_only=True)
    image_1536x1536 = serializers.ImageField(read_only=True)
    image_1024x480 = serializers.ImageField(read_only=True)
    image_1536x660 = serializers.ImageField(read_only=True)
    image_2048x800 = serializers.ImageField(read_only=True)
    image_2560x940 = serializers.ImageField(read_only=True)
    image_3072x940 = serializers.ImageField(read_only=True)



class ProductInstanceNameSerializer(serializers.ModelSerializer):
    """
    A serializer to display name of (sub)categories
    """

    class Meta:
        model = Product
        fields = ['name']
        read_only_fields = fields


class ProductColorSerializer(serializers.ModelSerializer):
    """
    A serializer to display name of (sub)categories
    """

    class Meta:
        model = ProductColor
        fields = ('name', 'color_hex')
        read_only_fields = fields


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    A serializer to append available variants to product
    """

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('name', 'thumbnail', 'image')
        read_only_fields = fields


class ProductListByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display products by (sub)category
    """

    unit = serializers.SerializerMethodField()
    categories = ProductInstanceNameSerializer(source='category', read_only=True, many=True)
    colors = ProductColorSerializer(read_only=True, many=True)
    styles = ProductInstanceNameSerializer(read_only=True, many=True)
    applications = ProductInstanceNameSerializer(read_only=True, many=True)
    materials = ProductInstanceNameSerializer(read_only=True, many=True)
    variants = ProductVariantSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'unit',
            'gross_price',
            'can_be_purchased_online',
            'categories',
            'colors',
            'styles',
            'applications',
            'materials',
            'thumbnail',
            'variants'
        )
        read_only_fields = fields

    
    def get_unit(self, product):
        return product.get_unit_display()
