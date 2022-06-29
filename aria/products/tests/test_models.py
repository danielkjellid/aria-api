import pytest
from model_bakery import baker

from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Color, Product, ProductOption, Shape, Size, Variant
from aria.suppliers.models import Supplier

pytestmark = pytest.mark.django_db


class TestProductsModels:
    def test_product_model_create(self) -> None:
        """
        Test creation of product instance.
        """

        supplier = baker.make(Supplier)

        options = {
            "name": "Test product",
            "supplier": supplier,
            "status": ProductStatus.AVAILABLE,
            "slug": "1-test-product",
            "short_description": "Testing",
            "description": "More testing",
            "new_description": "Even more testing",  # TODO: Rename to description
            "unit": ProductUnit.PCS,
            "available_in_special_sizes": True,
            "absorption": 0.00,
        }

        product = Product.objects.create(**options)

        assert product.name == "Test product"
        assert product.supplier == supplier
        assert product.status == ProductStatus.AVAILABLE
        assert product.slug == "1-test-product"
        assert product.short_description == "Testing"
        assert product.description == "More testing"
        assert product.new_description == "Even more testing"
        assert product.unit == ProductUnit.PCS
        assert product.vat_rate == 0.25  # 0.25 is default
        assert product.available_in_special_sizes is True
        assert product.absorption == 0.00
        assert product.is_imported_from_external_source is False  # False is default

    def test_size_model_create(self) -> None:
        """
        Test creation of size instance.
        """

        width_height_depth = {
            "width": 10,
            "height": 10,
            "depth": 10,
        }

        width_height = {"width": 20, "height": 20}

        circumference = {"circumference": 30}

        product_1 = Size.objects.create(**width_height_depth)
        product_2 = Size.objects.create(**width_height)
        product_3 = Size.objects.create(**circumference)

        assert product_1.width == 10
        assert product_1.height == 10
        assert product_1.depth == 10
        assert product_1.circumference is None

        assert product_2.width == 20
        assert product_2.height == 20
        assert product_2.depth is None
        assert product_2.circumference is None

        assert product_3.width is None
        assert product_3.height is None
        assert product_3.depth is None
        assert product_3.circumference == 30

    def test_variant_model_create(self) -> None:
        """
        Test creation of variant instance.
        """

        options = {"name": "Some Variant", "is_standard": False}

        variant = Variant.objects.create(**options)

        assert variant.name == "Some Variant"
        assert variant.is_standard is False

    def test_color_model_create(self) -> None:
        """
        Test creation of color instance.
        """

        options = {"name": "Red", "color_hex": "#FFFFFF"}

        color = Color.objects.create(**options)

        assert color.name == "Red"
        assert color.color_hex == "#FFFFFF"

    def test_shape_model_create(self) -> None:
        """
        Test creation of shape instance.
        """

        shape = Shape.objects.create(name="Square")

        assert shape.name == "Square"

    def test_product_option_model_create(self) -> None:
        """
        Test creation of product option instance.
        """

        product = baker.make(Product)
        variant = baker.make(Variant)
        size = baker.make(Size)

        options = {
            "product": product,
            "variant": variant,
            "size": size,
            "gross_price": 100.00,
        }

        product_option = ProductOption.objects.create(**options)

        assert product_option.product == product
        assert product_option.variant == variant
        assert product_option.size == size
        assert product_option.gross_price == 100.00
        assert product_option.status == ProductStatus.AVAILABLE  # Default
