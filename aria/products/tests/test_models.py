from decimal import Decimal

import pytest

from aria.product_attributes.tests.utils import create_size, create_variant
from aria.products.enums import ProductStatus, ProductUnit
from aria.products.models import Product, ProductOption
from aria.products.tests.utils import create_product
from aria.suppliers.tests.utils import get_or_create_supplier

pytestmark = pytest.mark.django_db


class TestProductsModels:
    def test_product_model_create(self) -> None:
        """
        Test creation of product instance.
        """

        supplier = get_or_create_supplier()

        options = {
            "name": "Test product",
            "supplier": supplier,
            "status": ProductStatus.AVAILABLE,
            "slug": "1-test-product",
            "description": "Even more testing",
            "unit": ProductUnit.PCS,
            "available_in_special_sizes": True,
            "absorption": 0.00,
        }

        product = Product.objects.create(**options)

        assert product.name == "Test product"
        assert product.supplier == supplier
        assert product.status == ProductStatus.AVAILABLE
        assert product.slug == "1-test-product"
        assert product.description == "Even more testing"
        assert product.unit == ProductUnit.PCS
        assert product.vat_rate == 0.25  # 0.25 is default
        assert product.available_in_special_sizes is True
        assert product.absorption == 0.00
        assert product.is_imported_from_external_source is False  # False is default

    def test_product_option_model_create(self) -> None:
        """
        Test creation of product option instance.
        """

        product = create_product()
        variant = create_variant()
        size = create_size(width=Decimal("100.0"), height=Decimal("100.0"))

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
