from inventory.models import (Category, Product, ProductColor, ProductFile,
                              ProductImage, ProductSize, ProductVariant,
                              SubCategory, Supplier)
from rest_framework import serializers


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


class CategorySerializer(serializers.Serializer):
    """
    A serializer to display a specific category instance
    """

    name = serializers.CharField(read_only=True)
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
        fields = ('id', 'name', 'thumbnail', 'image', 'additional_cost')
        read_only_fields = fields

    
class ProductSizeSerializer(serializers.ModelSerializer):
    """
    A serializer to append available sizes to product
    """

    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductSize
        fields = ('id', 'name')
        read_only_fields = fields

    def get_name(self, instance):
        if instance.depth is not None:
            name = 'B%s x H%s x D%s' % (instance.width, instance.height, instance.depth)
            return name.strip()

        name = 'B%s x H%s' % (instance.width, instance.height)
        return name.strip()


class ProductFileSerializer(serializers.ModelSerializer):
    """
    A serializer to append files to product
    """

    class Meta:
        model = ProductFile
        fields = ('name', 'file')
        read_only_fields = fields


class ProductImageSerializer(serializers.ModelSerializer):

    image_512x512 = serializers.ImageField(read_only=True)
    image_1024x1024 = serializers.ImageField(read_only=True)
    image_1024x480 = serializers.ImageField(read_only=True)
    image_1536x660 = serializers.ImageField(read_only=True)
    image_2048x800 = serializers.ImageField(read_only=True)
    image_2560x940 = serializers.ImageField(read_only=True)
    image_3072x940 = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductImage
        fields = (
            'image_512x512',
            'image_1024x1024',
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

    unit = serializers.SerializerMethodField()
    categories = ProductInstanceNameSerializer(source='category', read_only=True, many=True)
    colors = ProductColorSerializer(read_only=True, many=True)
    styles = ProductInstanceNameSerializer(read_only=True, many=True)
    applications = ProductInstanceNameSerializer(read_only=True, many=True)
    materials = ProductInstanceNameSerializer(read_only=True, many=True)
    variants = ProductVariantSerializer(read_only=True, many=True)
    gross_price = serializers.SerializerMethodField()

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

    
    def get_gross_price(self, product):
        formatted_price = '%0.2f' % (product.gross_price)

        return formatted_price.strip()


class ProductSerializer(serializers.ModelSerializer):
    """
    A serializer to get a single product instance
    """

    unit = serializers.SerializerMethodField()
    colors = ProductInstanceNameSerializer(read_only=True, many=True)
    styles = ProductInstanceNameSerializer(read_only=True, many=True)
    applications = ProductInstanceNameSerializer(read_only=True, many=True)
    materials = ProductInstanceNameSerializer(read_only=True, many=True)
    sizes = ProductSizeSerializer(read_only=True, many=True)
    gross_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(read_only=True, many=True)
    variants = ProductVariantSerializer(read_only=True, many=True)
    files = ProductFileSerializer(read_only=True, many=True)
    origin_country = serializers.StringRelatedField(source='supplier.origin_country', read_only=True )

    class Meta:
        model = Product
        fields = (
            'id',
            'unit',
            'name',
            'slug',
            'short_description',
            'description',
            'gross_price',
            'available_in_special_sizes',
            'absorption',
            'can_be_purchased_online',
            'sizes',
            'colors',
            'styles',
            'applications',
            'materials',
            'images',
            'variants',
            'files',
            'origin_country'
        )

    def get_unit(self, product):
        """
        Return display name of unit type
        """

        return product.get_unit_display()

    def get_gross_price(self, product):
        """
        Format price to always have two decimals
        """
        
        formatted_price = '%0.2f' % (product.gross_price)

        return formatted_price.strip()
