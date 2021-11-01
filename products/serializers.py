import os
from django.conf import settings

from products.models import Product, ProductSiteState, ProductFile, ProductImage, ProductVariant, ProductSize
from rest_framework import serializers

class InstanceColorSerializer(serializers.Serializer):
    """
    A serializer to display name and color hex
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    color_hex = serializers.CharField(read_only=True)


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


class ProductSizeSerializer(serializers.ModelSerializer):
    """
    A serializer to append available sizes to product
    """

    name = serializers.StringRelatedField(source='size', read_only=True)

    class Meta:
        model = ProductSize
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
            'apply_filter',
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
    styles = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(read_only=True, many=True)
    site_state = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'unit',
            'categories',
            'colors',
            'styles',
            'applications',
            'materials',
            'thumbnail',
            'variants',
            'site_state'
        )
        read_only_fields = fields

    
    def get_unit(self, product):
        return product.get_unit_display()

    def get_site_state(self, product):
        site_state = ProductSiteState.on_site.get(product=product)

        return ProductSiteStateSerializer(site_state, read_only=True).data

    def get_styles(self, product):
        styles = product.get_styles_display()

        return ProductInstanceNameSerializer(styles, read_only=True, many=True).data


    def get_applications(self, product):
        applications = product.get_applications_display()

        return ProductInstanceNameSerializer(applications, read_only=True, many=True).data

    def get_materials(self, product):
        materials = product.get_materials_display()

        return ProductInstanceNameSerializer(materials, read_only=True, many=True).data

    
class ProductSiteStateSerializer(serializers.ModelSerializer):

    gross_price = serializers.SerializerMethodField()
    class Meta:
        model = ProductSiteState
        fields = (
            'gross_price',
            'display_price',
            'can_be_purchased_online',
            'can_be_picked_up',
        )
        read_only_fields = fields

    def get_gross_price(self, instance):
        """
        Format price to always have two decimals
        """
        formatted_price = '%0.2f' % (instance.gross_price)

        return formatted_price.strip()

class ProductSerializer(serializers.ModelSerializer):
    """
    A serializer to get a single product instance
    """

    unit = serializers.SerializerMethodField()
    colors = ProductInstanceNameSerializer(read_only=True, many=True)
    styles = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    images = ProductImageSerializer(read_only=True, many=True)
    variants = ProductVariantSerializer(read_only=True, many=True)
    files = ProductFileSerializer(read_only=True, many=True)
    origin_country = serializers.StringRelatedField(source='supplier.origin_country', read_only=True )
    site_state = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'unit',
            'name',
            'slug',
            'short_description',
            'description',
            'available_in_special_sizes',
            'absorption',
            'sizes',
            'colors',
            'styles',
            'applications',
            'materials',
            'images',
            'variants',
            'files',
            'origin_country',
            'site_state'
        )
        read_only_fields = fields

    def get_unit(self, product):
        """
        Return display name of unit type
        """

        return product.get_unit_display()

    def get_sizes(self, product):
        """
        Order sizes based on width
        """

        sizes = product.sizes.all().order_by('size')
        return ProductSizeSerializer(sizes, read_only=True, many=True).data

    def get_site_state(self, product):
        site_state = ProductSiteState.on_site.get(product=product)

        return ProductSiteStateSerializer(site_state, read_only=True).data

    def get_styles(self, product):
        styles = product.get_styles_display()

        return ProductInstanceNameSerializer(styles, read_only=True, many=True).data


    def get_applications(self, product):
        applications = product.get_applications_display()

        return ProductInstanceNameSerializer(applications, read_only=True, many=True).data

    def get_materials(self, product):
        materials = product.get_materials_display()

        return ProductInstanceNameSerializer(materials, read_only=True, many=True).data


class ProductNameImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'name',
            'thumbnail'
        )


class ProductListSerializer(serializers.ModelSerializer):
    
    product = ProductNameImageSerializer(source='*')
    unit = serializers.CharField(source='get_unit_display')
    status = serializers.CharField(source='get_status_display') # get display name of integer choice 
    variants = ProductVariantSerializer(read_only=True, many=True)
    site_state = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'product',
            'unit',
            'status',
            'variants',
            'site_state'
        )

    def get_site_state(self, product):
        site_state = ProductSiteState.on_site.get(product=product)

        return ProductSiteStateSerializer(site_state, read_only=True).data