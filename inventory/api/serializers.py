import os
from django.conf import settings

from inventory.models.category import Category, SubCategory
from inventory.models.supplier import Supplier
from inventory.models.product import Product, ProductColor, ProductFile, ProductImage, ProductVariant, ProductVariantSize
from inventory.models.kitchen import Kitchen
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
        children = instance.children.all().order_by('ordering')
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


# product serializers
class ProductInstanceNameSerializer(serializers.ModelSerializer):
    """
    A serializer to display name of (sub)categories
    """

    class Meta:
        model = Product
        fields = ['name']
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


class ProductVariantSizeSerializer(serializers.ModelSerializer):
    """
    A serializer to append available sizes to product
    """

    name = serializers.StringRelatedField(source='size', read_only=True)

    class Meta:
        model = ProductVariantSize
        fields = ('id', 'name', 'additional_cost')
        read_only_fields = fields


class ProductFileSerializer(serializers.ModelSerializer):
    """
    A serializer to append files to product
    """

    class Meta:
        model = ProductFile
        fields = ('name', 'file')
        read_only_fields = fields


class ProductImageSerializer(serializers.ModelSerializer):

    image_512x512 = serializers.SerializerMethodField()
    image_1024x1024 = serializers.SerializerMethodField()
    image_1024x480 = serializers.SerializerMethodField()
    image_1536x660 = serializers.SerializerMethodField()
    image_2048x800 = serializers.SerializerMethodField()
    image_2560x940 = serializers.SerializerMethodField()
    image_3072x940 = serializers.SerializerMethodField()

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

    def get_image_512x512(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_512x512))

    def get_image_1024x1024(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_1024x1024))

    def get_image_1024x480(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_1024x480))

    def get_image_1536x660(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_1536x660))

    def get_image_2048x800(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_2048x800))

    def get_image_2560x940(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_2560x940))

    def get_image_3072x940(self, image):
        return os.path.join(settings.MEDIA_URL, str(image.image_3072x940))


class ProductListByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display products by (sub)category
    """

    unit = serializers.SerializerMethodField()
    categories = ProductInstanceNameSerializer(source='category', read_only=True, many=True)
    colors = InstanceColorSerializer(read_only=True, many=True)
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
    sizes = serializers.SerializerMethodField()
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
        read_only_fields = fields

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

    def get_sizes(self, product):
        """
        Order sizes based on width
        """

        sizes = product.sizes.all().order_by('size')
        return ProductVariantSizeSerializer(sizes, read_only=True, many=True).data


# kitchen serializers
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
            'id',
            'name',
            'slug',
            'thumbnail_description',
            'thumbnail_500x305',
            'thumbnail_660x400',
            'thumbnail_850x520'
        )
        read_only_fields = fields


class KitchenVariantImageSerializer(serializers.Serializer):
    """
    Serializer for kitchen variants which uses an image instead of a color
    """

    name = serializers.CharField(read_only=True)
    image = serializers.ImageField()



class KitchenSerializer(serializers.ModelSerializer):
    """
    Serializer for getting a specific kitchen instance
    """

    example_from_price = serializers.SerializerMethodField()
    silk_variants = InstanceColorSerializer(read_only=True, many=True)
    decor_variants = KitchenVariantImageSerializer(read_only=True, many=True)
    plywood_variants = KitchenVariantImageSerializer(read_only=True, many=True)
    laminate_variants = InstanceColorSerializer(read_only=True, many=True)
    exclusive_variants = InstanceColorSerializer(read_only=True, many=True)
    trend_variants = InstanceColorSerializer(read_only=True, many=True)
    image_512x512 = serializers.ImageField(read_only=True)
    image_1024x1024 = serializers.ImageField(read_only=True)
    image_1536x1536 = serializers.ImageField(read_only=True)
    image_1024x480 = serializers.ImageField(read_only=True)
    image_1536x660 = serializers.ImageField(read_only=True)
    image_2048x800 = serializers.ImageField(read_only=True)
    image_2560x940 = serializers.ImageField(read_only=True)
    image_3072x940 = serializers.ImageField(read_only=True)

    class Meta:
        model = Kitchen
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'extra_description',
            'example_from_price',
            'can_be_painted',
            'silk_variants',
            'decor_variants',
            'plywood_variants',
            'laminate_variants',
            'exclusive_variants',
            'trend_variants',
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

    def get_example_from_price(self, instance):

        if instance.example_from_price:
            formatted_from_price = '%0.2f' % (instance.example_from_price)

            return formatted_from_price
        
        return None
