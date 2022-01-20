from rest_framework import serializers

from aria.core.serializers import BaseHeaderImageSerializer
from aria.products.models import (
    Product,
    ProductFile,
    ProductOption,
    Size,
    Variant,
)
from aria.products.selectors import (
    get_related_unique_variants,
)


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
        fields = ["name"]
        read_only_fields = fields


class VariantSerializer(serializers.ModelSerializer):

    image = serializers.CharField(source="image.url", read_only=True)

    class Meta:
        model = Variant
        fields = ("id", "name", "thumbnail", "image")
        read_only_fields = fields


class SizeSerializer(serializers.ModelSerializer):

    name = serializers.StringRelatedField(source="*")

    class Meta:
        model = Size
        fields = ("id", "name")
        read_only_fields = fields


class ProductOptionSerializer(serializers.ModelSerializer):
    """
    A serializer to dispay current options (combination of variants)
    and sizes, and additional price, if any
    """

    variant = VariantSerializer(read_only=True)
    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductOption
        fields = ("id", "variant", "size", "gross_price")


class ProductFileSerializer(serializers.ModelSerializer):
    """
    A serializer to append files to product
    """

    class Meta:
        model = ProductFile
        fields = ("name", "file")
        read_only_fields = fields


class ProductListByCategorySerializer(serializers.ModelSerializer):
    """
    A serializer to display products by (sub)category
    """

    unit = serializers.SerializerMethodField()
    categories = ProductInstanceNameSerializer(
        source="category", read_only=True, many=True
    )
    colors = InstanceColorSerializer(read_only=True, many=True)
    styles = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    from_price = serializers.DecimalField(
        source="get_lowest_option_price",
        decimal_places=2,
        coerce_to_string=True,
        max_digits=8,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "unit",
            "categories",
            "colors",
            "styles",
            "applications",
            "materials",
            "thumbnail",
            "variants",
            "from_price",
            "display_price",
        )
        read_only_fields = fields

    def get_unit(self, product):
        return product.get_unit_display()

    def get_styles(self, product):
        styles = product.get_styles_display()

        return ProductInstanceNameSerializer(styles, read_only=True, many=True).data

    def get_applications(self, product):
        applications = product.get_applications_display()

        return ProductInstanceNameSerializer(
            applications, read_only=True, many=True
        ).data

    def get_materials(self, product):
        materials = product.get_materials_display()

        return ProductInstanceNameSerializer(materials, read_only=True, many=True).data

    def get_variants(self, product):
        product_variants = get_related_unique_variants(product=product)

        return VariantSerializer(product_variants, read_only=True, many=True).data


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
    images = BaseHeaderImageSerializer(read_only=True, many=True)
    variants = serializers.SerializerMethodField()
    files = ProductFileSerializer(read_only=True, many=True)
    origin_country = serializers.StringRelatedField(
        source="supplier.origin_country", read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "unit",
            "name",
            "slug",
            "short_description",
            "description",
            "available_in_special_sizes",
            "absorption",
            "sizes",
            "colors",
            "styles",
            "applications",
            "materials",
            "images",
            "variants",
            "files",
            "origin_country",
            "display_price",
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

        sizes = (
            Size.objects.filter(product_options__product=product)
            .distinct()
            .order_by("width", "height", "depth", "circumference")
        )
        return SizeSerializer(sizes, read_only=True, many=True).data

    def get_styles(self, product):
        styles = product.get_styles_display()

        return ProductInstanceNameSerializer(styles, read_only=True, many=True).data

    def get_applications(self, product):
        applications = product.get_applications_display()

        return ProductInstanceNameSerializer(
            applications, read_only=True, many=True
        ).data

    def get_materials(self, product):
        materials = product.get_materials_display()

        return ProductInstanceNameSerializer(materials, read_only=True, many=True).data

    def get_variants(self, product):
        product_variants = get_related_unique_variants(product=product)

        return VariantSerializer(product_variants, read_only=True, many=True).data


class ProductNameImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "thumbnail")


class ProductListSerializer(serializers.ModelSerializer):

    product = ProductNameImageSerializer(source="*")
    unit = serializers.CharField(source="get_unit_display")
    status = serializers.CharField(
        source="get_status_display"
    )  # get display name of integer choice
    variants = serializers.SerializerMethodField()
    from_price = serializers.DecimalField(
        source="get_lowest_option_price",
        decimal_places=2,
        coerce_to_string=True,
        max_digits=8,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "product",
            "unit",
            "status",
            "variants",
            "from_price",
            "display_price",
        )

    def get_variants(self, product):
        product_variants = get_related_unique_variants(product=product)

        return VariantSerializer(product_variants, read_only=True, many=True).data
