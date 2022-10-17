from decimal import Decimal

import pytest

from aria.products.models import Variant
from aria.products.services.product_options import (
    product_option_create,
    product_option_delete_related_variants,
)
from aria.products.tests.utils import (
    create_product,
    create_product_option,
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
        assert False

    def test_service_product_option_bulk_create_options_and_sizes(
        self, django_assert_max_num_queries
    ):
        """
        Test that the product_option_bulk_create_options_and_sizes creates multiple
        product options and sizes not already existing effectively and within query
        limits.
        """
        assert False

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
