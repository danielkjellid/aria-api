from decimal import Decimal

import pytest

from aria.products.enums import ProductStatus
from aria.products.models import Size, Variant
from aria.products.records import OptionRecord, SizeRecord
from aria.products.services.product_options import (
    product_option_bulk_create,
    product_option_create,
    product_option_delete_related_variants,
    product_options_bulk_create_options_and_sizes,
)
from aria.products.tests.utils import (
    create_product,
    create_product_option,
    create_size,
    create_variant,
)

pytestmark = pytest.mark.django_db


class TestProductOptionsServices:
    def test_service_product_option_create(self, django_assert_max_num_queries):
        """
        Test that the product_option_create creates a product option within query
        limits.
        """

        product = create_product()
        variant = create_variant()

        product_options_count = product.options.count()

        with django_assert_max_num_queries(3):
            option_record = product_option_create(
                product=product,
                gross_price=Decimal("100.0"),
                size=None,
                variant=variant,
            )

        assert product.options.count() == product_options_count + 1
        assert option_record.variant_id == variant.id

    def test_service_product_option_bulk_create(self, django_assert_max_num_queries):
        """
        Test that the product_option_bulk_create creates multiple product options
        effectively and within query limits.
        """

        product = create_product()
        size_1 = create_size(width=Decimal("20.0"), height=Decimal("50.0"))
        size_2 = create_size(circumference=Decimal("30.0"))
        variant = create_variant(name="Test variant")

        product_options_count = product.options.count()

        payload = [
            {
                "status": ProductStatus.AVAILABLE,
                "gross_price": 500.0,
                "size_id": size_1.id,
                "variant_id": variant.id,
            },
            {
                "status": ProductStatus.AVAILABLE,
                "gross_price": 400.0,
                "size_id": size_2.id,
                "variant_id": None,
            },
            {
                "status": ProductStatus.AVAILABLE,
                "gross_price": 500.0,
                "size_id": None,
                "variant_id": variant.id,
            },
        ]

        with django_assert_max_num_queries(1):
            created_options = product_option_bulk_create(
                product=product, product_options=payload
            )

        assert len(created_options) == 3
        assert product.options.count() == product_options_count + 3

    def test_service_product_option_bulk_create_options_and_sizes(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_option_bulk_create_options_and_sizes creates multiple
        product options and sizes not already existing effectively and within query
        limits.
        """

        product = create_product(options=[])
        variant = create_variant(name="Test variant")

        create_size(width=Decimal("20.0"), height=Decimal("50.0"))
        create_size(circumference=Decimal("30.0"))

        product_options_count = product.options.count()
        sizes_in_db_count = Size.objects.count()

        payload = [
            OptionRecord(
                status=ProductStatus.AVAILABLE,
                gross_price=500.0,
                variant_id=variant.id,
                size=SizeRecord(  # Size already exists, should not create duplicate.
                    width=20.0,
                    height=50.0,
                    depth=None,
                    circumference=None,
                ),
            ),
            OptionRecord(
                status=ProductStatus.AVAILABLE,
                gross_price=400.0,
                variant_id=variant.id,
                size=SizeRecord(  # Size already exists, should not create duplicate.
                    width=None,
                    height=None,
                    depth=None,
                    circumference=30.0,
                ),
            ),
            OptionRecord(
                status=ProductStatus.AVAILABLE,
                gross_price=300.0,
                variant_id=variant.id,
                size=SizeRecord(
                    width=102.0,
                    height=90.0,
                    depth=None,
                    circumference=None,
                ),
            ),
            OptionRecord(
                status=ProductStatus.AVAILABLE,
                gross_price=200.0,
                variant_id=variant.id,
                size=None,
            ),
            OptionRecord(
                status=ProductStatus.AVAILABLE,
                gross_price=100.0,
                variant_id=variant.id,
                size=SizeRecord(
                    width=25.0, height=30.0, depth=10.0, circumference=None
                ),
            ),
        ]

        with django_assert_max_num_queries(4):
            created_options_sizes = product_options_bulk_create_options_and_sizes(
                product=product, options=payload
            )

        assert len(created_options_sizes) == 5
        assert product.options.count() == product_options_count + 5
        assert Size.objects.count() == sizes_in_db_count + 2

    def test_service_product_option_delete_related_variants_deletes_variants(
        self, django_assert_max_num_queries
    ) -> None:
        """
        Test that we delete dangling variants after deleting the parent
        product option.
        """

        product = create_product()

        product_option_1 = create_product_option(product=product)
        product_option_2 = create_product_option(product=product)
        product_option_3 = create_product_option(product=product)

        variant_1 = create_variant()
        variant_2 = create_variant()

        # Create two product options with the same variant to test
        # that we do NOT delete variant_1. We do not want to delete
        # it when other product options are using it.
        product_option_1.variant = variant_1
        product_option_1.save(update_fields=["variant"])

        product_option_2.variant = variant_1
        product_option_2.save(update_fields=["variant"])

        # Create a separate instance where we want to test that we
        # actually delete the variant.
        product_option_3.variant = variant_2
        product_option_3.save(update_fields=["variant"])

        with django_assert_max_num_queries(1):
            product_option_delete_related_variants(instance=product_option_1)
        with django_assert_max_num_queries(4):
            product_option_delete_related_variants(instance=product_option_3)

        # Assert that variant_1 wasn't deleted.
        assert Variant.objects.filter(id=variant_1.id).exists()

        # Assert that variant_2 was deleted.
        with pytest.raises(Variant.DoesNotExist):
            Variant.objects.get(id=variant_2.id)
